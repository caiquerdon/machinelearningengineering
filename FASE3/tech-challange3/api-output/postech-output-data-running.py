import boto3
import csv
import io
import json
import os

BUCKET = "postech-data-running"
KEY = "model/outuput/tabela_final_atletas_com_modelos.csv"

s3 = boto3.client("s3")

_CACHE = {"loaded": False, "rows": [], "index": {}, "total": 0}

def _cors_headers():
    return {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

def _ok(body: dict, status=200):
    return {
        "statusCode": status,
        "headers": _cors_headers(),
        "body": json.dumps(body, ensure_ascii=False)
    }

def _err(code: str, message: str, http_status: int, details: dict | None = None):
    payload = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return _ok(payload, status=http_status)

def _load_csv():
    if _CACHE["loaded"]:
        return
    local_path = "/tmp/athletes.csv"
    if not os.path.exists(local_path):
        obj = s3.get_object(Bucket=BUCKET, Key=KEY)
        body = obj["Body"].read()
        with open(local_path, "wb") as f:
            f.write(body)
    with open(local_path, "rb") as f:
        content = f.read()
    buf = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(buf)

    rows, index = [], {}
    for r in reader:
        athlete_id = str(r.get("athlete") or r.get("athlete_id") or "").strip()
        y_raw = r.get("y_proxy")
        try:
            y_proxy = 1 if float(y_raw) >= 0.5 else 0
        except:
            y_proxy = 0
        if athlete_id:
            row = {"athlete_id": athlete_id, "y_proxy": y_proxy}
            rows.append(row)
            index[athlete_id] = row

    _CACHE.update(loaded=True, rows=rows, index=index, total=len(rows))

def lambda_handler(event, context):
    
    method = (event.get("httpMethod")
              or event.get("requestContext", {}).get("http", {}).get("method"))
    if method == "OPTIONS":
        return _ok({}, 204)

    path = (event.get("rawPath") or event.get("path") or "/").rstrip("/")
    qs = event.get("queryStringParameters") or {}

    
    if path.endswith("/health"):
        return _ok({"data": {"status": "ok"}})

    try:
        _load_csv()
    except Exception as e:
        return _err("INTERNAL_ERROR", "Falha ao carregar dados de origem.", 500, {"detail": str(e)})

    
    if path.endswith("/athletes") or path.endswith("/athletes/all"):
        
        want_all = (
            path.endswith("/athletes/all")
            or str(qs.get("all", "")).lower() in ("1", "true", "yes")
            or str(qs.get("limit", "")).lower() in ("0", "-1", "all")
        )

        if want_all:
            data = [{"athlete_id": r["athlete_id"]} for r in _CACHE["rows"]]
            return _ok({
                "data": data,
                "meta": {"count": len(data), "total": _CACHE["total"]},
                "links": {"self": "/athletes?all=true"}
            })

        
        try:
            limit = max(1, min(200, int(qs.get("limit", 50))))
        except:
            return _err("BAD_REQUEST", "Parâmetro 'limit' inválido.", 400, {"limit": qs.get("limit")})
        try:
            offset = max(0, int(qs.get("offset", 0)))
        except:
            return _err("BAD_REQUEST", "Parâmetro 'offset' inválido.", 400, {"offset": qs.get("offset")})

        slice_ = _CACHE["rows"][offset: offset + limit]
        data = [{"athlete_id": r["athlete_id"]} for r in slice_]

        next_offset = offset + limit
        links = {"self": f"/athletes?limit={limit}&offset={offset}"}
        if next_offset < _CACHE["total"]:
            links["next"] = f"/athletes?limit={limit}&offset={next_offset}"

        return _ok({
            "data": data,
            "meta": {"count": len(data), "limit": limit, "offset": offset, "total": _CACHE["total"]},
            "links": links
        })

    
    if path.endswith("/predict"):
        athlete_id = (qs.get("athlete") or "").strip()
        if not athlete_id:
            return _err("BAD_REQUEST", "Parâmetro 'athlete' é obrigatório.", 400)

        row = _CACHE["index"].get(athlete_id)
        if not row:
            return _err("NOT_FOUND", "Atleta não encontrado.", 404, {"athlete_id": athlete_id})

        ready = row["y_proxy"] == 1
        message = "O atleta está pronto para a Maratona" if ready else "O atleta não está pronto para a Maratona"

        return _ok({"data": {"athlete_id": athlete_id, "ready": ready, "message": message}})

    return _err("ROUTE_NOT_FOUND", "Rota não encontrada. Use /athletes, /athletes/all, /predict ou /health.", 404)
