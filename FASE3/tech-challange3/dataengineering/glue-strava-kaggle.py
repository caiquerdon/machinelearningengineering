# Importate
# Para este job sao passados os seguintes input arguments:


# Key: Value
# --enable-glue-datacatalog: true
# --job-bookmark-option: job-bookmark-disable
# --TempDir: s3://aws-glue-assets-891377116984-us-east-1/temporary/
# --secret_name: kaggle/creds
# --enable-metrics: true
# --enable-spark-ui: true
# --spark-event-logs-path: s3://aws-glue-assets-891377116984-us-east-1/sparkHistoryLogs/
# --enable-job-insights: true
# --output_s3: s3://postech-data-running/strava/curated/
# --additional-python-modules: kaggle==1.6.17,pyarrow,fastparquet
# --enable-observability-metrics: true
# --dataset_slug: olegoaer/running-races-strava
# --job-language: python



import os
import json
import uuid
import tempfile
from datetime import datetime
import argparse
import boto3
from botocore.exceptions import ClientError
from pyspark.sql import SparkSession, functions as F


def parse_args():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--dataset_slug", default="olegoaer/running-races-strava")
    p.add_argument("--secret_name",  default="kaggle/creds")
    p.add_argument("--output_s3",    required=True)
    p.add_argument("--write_mode",   default="overwrite", choices=["overwrite", "append"])
    p.add_argument("--landing_mode", default="flat", choices=["flat", "run"])
    p.add_argument("--landing_base", default="s3://postech-data-running/strava/landing/")
    
    args, unknown = p.parse_known_args()
    if unknown:
        print(f"[warn] ignorando args do Glue: {unknown}")
    return args


def require_s3_uri(uri: str):
    if not uri or not uri.startswith("s3://"):
        raise ValueError("Informe um caminho S3 válido (ex.: s3://bucket/prefix/).")
    return uri

def get_kaggle_creds(secret_name: str):
    sm = boto3.client("secretsmanager")
    try:
        payload = sm.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(f"Erro ao ler segredo '{secret_name}': {e}") from e
    data = json.loads(payload["SecretString"])
    user = data.get("KAGGLE_USERNAME") or data.get("username")
    key  = data.get("KAGGLE_KEY")      or data.get("key")
    if not user or not key:
        raise ValueError("Segredo inválido: inclua KAGGLE_USERNAME e KAGGLE_KEY.")
    return user, key

def s3_split(uri: str):
    
    rest = uri[5:]
    bucket, _, key = rest.partition("/")
    return bucket, key

def upload_dir_to_s3(local_dir: str, s3_prefix: str):
    s3 = boto3.client("s3")
    bucket, key_prefix = s3_split(s3_prefix.rstrip("/") + "/")
    sent = 0
    for dp, _, files in os.walk(local_dir):
        for f in files:
            src = os.path.join(dp, f)
            rel = os.path.relpath(src, local_dir).replace("\\", "/")
            dst_key = f"{key_prefix}{rel}"
            s3.upload_file(src, bucket, dst_key)
            sent += 1
    print(f"[landing] {sent} arquivo(s) enviados para {s3_prefix}")
    return sent

def pick(cols, *cands):
    for c in cands:
        if c in cols:
            return c
    return None

def read_with_auto_sep(spark, paths):
    
    for sep in [",", "\t", ";", "|"]:
        df = spark.read.options(header=True, inferSchema=True, sep=sep).csv(paths)
        if len(df.columns) > 1:
            print(f"[read] separador detectado: '{sep}' ({len(df.columns)} colunas)")
            return df
    raise RuntimeError("Não foi possível detectar separador. Defina um explicitamente, se necessário.")


def main():
    args = parse_args()
    OUTPUT_S3 = require_s3_uri(args.output_s3)
    LANDING_BASE = require_s3_uri(args.landing_base)

    
    user, key = get_kaggle_creds(args.secret_name)
    os.environ["KAGGLE_USERNAME"] = user
    os.environ["KAGGLE_KEY"] = key

   
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    tmpdir = tempfile.mkdtemp()
    print(f"[kaggle] baixando '{args.dataset_slug}' …")
    api.dataset_download_files(args.dataset_slug, path=tmpdir, quiet=True, unzip=True)

   
    if args.landing_mode == "run":
        run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        landing_prefix = LANDING_BASE.rstrip("/") + f"/{run_id}/"
    else:
        landing_prefix = LANDING_BASE

    uploaded = upload_dir_to_s3(tmpdir, landing_prefix)
    if uploaded == 0:
        raise RuntimeError("Nenhum arquivo subiu para a landing.")

    
    data_globs = [
        landing_prefix + "**/*.csv",
        landing_prefix + "**/*.csv.gz",
        landing_prefix + "**/*.tsv",
        landing_prefix + "**/*.txt",
    ]

    
    spark = (
        SparkSession.builder
        .appName("running-kaggle-to-parquet")
        .getOrCreate()
    )

   
    df = None
    
    csv_paths = [landing_prefix]  
    try:
        df = read_with_auto_sep(spark, [landing_prefix])
    except Exception:
        pass

    
    if df is None:
        try:
            df = spark.read.options(header=True, inferSchema=True, sep="\t").csv([landing_prefix])
            if len(df.columns) <= 1:
                df = None
        except Exception:
            df = None

    if df is None or len(df.columns) == 0:
        raise RuntimeError("Nenhum dado legível encontrado no prefixo de landing.")

    print(f"[read] colunas: {len(df.columns)}")

    
    cols = df.columns
    c_distance = pick(cols, "distance (m)", "distance_m", "distance", "distance_meters")
    c_elapsed  = pick(cols, "elapsed time (s)", "elapsed_time_s", "elapsed_time", "moving_time")
    c_elev     = pick(cols, "elevation gain (m)", "elev_gain_m", "total_elevation_gain")
    c_hr       = pick(cols, "average heart rate (bpm)", "avg_heart_rate", "average_heartrate", "avg_hr")
    c_ts       = pick(cols, "timestamp", "start_date", "date", "time", "start_time")

    if c_distance: df = df.withColumn("distance_m_std", F.col(c_distance).cast("double"))
    if c_elapsed:  df = df.withColumn("elapsed_s_std",  F.col(c_elapsed).cast("double"))
    if c_elev:     df = df.withColumn("elev_gain_m_std",F.col(c_elev).cast("double"))
    if c_hr:       df = df.withColumn("avg_hr_std",     F.col(c_hr).cast("double"))

    if c_ts:
        df = df.withColumn("ts_parsed", F.to_timestamp(F.col(c_ts)))

   
    if "ts_parsed" in df.columns:
        df = df.withColumn("year",  F.year("ts_parsed")) \
               .withColumn("month", F.month("ts_parsed")) \
               .withColumn("day",   F.dayofmonth("ts_parsed"))

        null_parts = df.select("year", "month", "day").filter(
            F.col("year").isNull() | F.col("month").isNull() | F.col("day").isNull()
        ).limit(1).count() > 0
    else:
        null_parts = True

    if null_parts:
        df = df.withColumn("ingest_ts", F.current_timestamp()) \
               .withColumn("year",  F.year("ingest_ts")) \
               .withColumn("month", F.month("ingest_ts")) \
               .withColumn("day",   F.dayofmonth("ingest_ts"))
        print("[part] usando data de ingestão para particionar")

    
    if {"elapsed_s_std", "distance_m_std"}.issubset(set(df.columns)):
        df = df.withColumn(
            "pace_s_per_km",
            F.when((F.col("elapsed_s_std").isNotNull()) & (F.col("distance_m_std") > 0),
                   F.col("elapsed_s_std") / (F.col("distance_m_std") / 1000.0))
        ).withColumn(
            "speed_kmh",
            F.when((F.col("elapsed_s_std").isNotNull()) & (F.col("distance_m_std") > 0),
                   (F.col("distance_m_std") / 1000.0) / (F.col("elapsed_s_std") / 3600.0))
        )

    if {"elev_gain_m_std", "distance_m_std"}.issubset(set(df.columns)):
        df = df.withColumn(
            "elev_per_km",
            F.when((F.col("distance_m_std") > 0) & (F.col("elev_gain_m_std").isNotNull()),
                   F.col("elev_gain_m_std") / (F.col("distance_m_std") / 1000.0))
        )

    
    print(f"[write] parquet -> {OUTPUT_S3} (mode={args.write_mode}) partitionBy(year,month,day)")
    (df.write
       .mode(args.write_mode)
       .partitionBy("year", "month", "day")
       .parquet(OUTPUT_S3))

    print("[ok] concluído")
    print(f"landing: {landing_prefix}")
    print(f"curated: {OUTPUT_S3}")


if __name__ == "__main__":
    main()