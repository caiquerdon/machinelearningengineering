# Imports necessarios

import requests
import base64
import boto3
import os
from datetime import datetime
import pandas as pd
from io import StringIO, BytesIO

# Request na pagina da b3

response = requests.get(
    'https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetDownloadPortfolioDay/eyJpbmRleCI6IklCT1YiLCJsYW5ndWFnZSI6InB0LWJyIn0='
)

# Decode base64 para texto

csv_text = base64.b64decode(response.content).decode('utf-8', errors='ignore')

# Ajustando as linhas do csv

lines = csv_text.splitlines()
lines = [line.rstrip(';') for line in lines]

# Ajustando o cabecalho

header = lines[1] + ";lixo"
csv_cleaned = "\n".join([header] + lines[2:])  # ignora linha 0, mantém 1 (ajustada) + dados


df = pd.read_csv(
    StringIO(csv_cleaned),
    sep=';',
    engine='python',
    on_bad_lines='skip'
)

# Remove as colunas nao necessarias ("lixo")
if "lixo" in df.columns:
    df.drop(columns=["lixo"], inplace=True)

# Ajusta o dataframe antes de salvar (remove caracteres especiais e acentos) 
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(' ', '_')
    .str.replace(r'[^\w]', '', regex=True)  # remove caracteres especiais
    .str.normalize('NFKD')                  # remove acentos
)   
    
# Particionamento utilizando o datetime
today = datetime.utcnow()
year = today.strftime('%Y')
month = today.strftime('%m')
day = today.strftime('%d')

# Convertando para parquet em memoria
parquet_buffer = BytesIO()
df.to_parquet(parquet_buffer, index=False, engine='pyarrow')

# Armazenando no s3
bucket_name = os.environ.get('S3_BUCKET', 'b3-dados-pregao-fiap-2025')
s3_key = f'b3/index=IBOV/year={year}/month={month}/day={day}/output.parquet'

s3 = boto3.client('s3')
s3.put_object(
    Bucket=bucket_name,
    Key=s3_key,
    Body=parquet_buffer.getvalue()
)

# Print final
print(f"Arquivo parquet enviado com sucesso para s3://{bucket_name}/{s3_key}")