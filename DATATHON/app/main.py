import time
import uuid
import logging
from pathlib import Path
from typing import Optional

from flask import Flask, request, g, send_file
from flask_restx import Api, Namespace, Resource, fields

from app.model_runtime import load_model, predict_one, MODEL_VERSION
from app.validation import validate_features


def create_app():
    app = Flask(__name__)

    # ----- Logging: usa logger do gunicorn quando disponível -----
    gunicorn_logger = logging.getLogger("gunicorn.error")
    logger = gunicorn_logger if gunicorn_logger.handlers else logging.getLogger("datathon-api")
    logger.setLevel(logging.INFO)

    # ----- Modelo: carrega uma vez no startup -----
    model = load_model()

    # ----- Swagger / OpenAPI -----
    api = Api(
        app,
        version="1.0.0",
        title="Datathon ML Inference API",
        description=(
            "API de inferência (online) para classificação de risco.\n\n"
            "**Como usar:** envie um JSON no endpoint **POST /predict** com `features`.\n"
            "O payload pode ser **parcial**: colunas ausentes serão imputadas pelo pipeline treinado.\n\n"
            "**Monitoramento:**\n"
            "- Endpoint `/monitoring` retorna o dashboard de drift.\n\n"
            "**Headers úteis:**\n"
            "- `X-Request-Id` (opcional): id de rastreio da requisição.\n\n"
            "**Respostas:**\n"
            "- `risk_score` é a probabilidade da classe positiva.\n"
            "- `prediction` é 0/1 após aplicar o `threshold_final` do treinamento.\n"
        ),
        doc="/docs",
        contact="Grupo Datathon - Pós-Tech ML Engineering",
    )

    # ----- Modelos comuns -----
    error_response = api.model(
        "ErrorResponse",
        {
            "error": fields.String(description="Mensagem de erro", example="Formato inválido."),
            "request_id": fields.String(description="ID de rastreio", example="test-123"),
        },
    )

    home_response = api.model(
        "HomeResponse",
        {
            "message": fields.String(example="API no ar. Use /health, /predict, /monitoring e /docs"),
            "docs": fields.String(example="/docs"),
        },
    )

    health_response = api.model(
        "HealthResponse",
        {
            "status": fields.String(example="ok"),
            "model_version": fields.String(example=MODEL_VERSION),
        },
    )

    predict_request = api.model(
        "PredictRequest",
        {
            "features": fields.Raw(
                required=True,
                description="Dicionário de features (pode ser parcial).",
                example={"Idade": 17},
            )
        },
    )

    predict_response = api.model(
        "PredictResponse",
        {
            "prediction": fields.Integer(description="Classe prevista (0/1)", example=0),
            "risk_score": fields.Float(description="Probabilidade da classe positiva", example=0.32),
            "model_version": fields.String(description="Versão do modelo", example=MODEL_VERSION),
            "request_id": fields.String(description="ID de rastreio", example="test-123"),
        },
    )

    # ----- Namespaces -----
    ns_meta = Namespace("meta", description="Metadados e saúde do serviço")
    ns_pred = Namespace("predictions", description="Inferência do modelo (online)")
    ns_monitor = Namespace("monitoring", description="Dashboard de monitoramento e drift")

    api.add_namespace(ns_meta, path="/")
    api.add_namespace(ns_pred, path="/")
    api.add_namespace(ns_monitor, path="/")

    # ----- Middleware request_id + timing -----
    @app.before_request
    def before_request():
        g.start_time = time.perf_counter()
        g.request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

    @app.after_request
    def after_request(response):
        elapsed_ms = (time.perf_counter() - g.start_time) * 1000.0

        logger.info(
            "request_id=%s method=%s path=%s status=%s elapsed_ms=%.2f ip=%s model_version=%s",
            getattr(g, "request_id", "-"),
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            request.remote_addr,
            MODEL_VERSION,
        )

        response.headers["X-Request-Id"] = getattr(g, "request_id", "-")
        return response

    # ----- Rotas -----
    @ns_meta.route("/")
    class Home(Resource):
        @ns_meta.marshal_with(home_response)
        def get(self):
            return {
                "message": "API no ar. Use /health, /predict, /monitoring e /docs",
                "docs": "/docs",
            }, 200

    @ns_meta.route("/health")
    class Health(Resource):
        @ns_meta.marshal_with(health_response)
        def get(self):
            return {"status": "ok", "model_version": MODEL_VERSION}, 200

    @ns_pred.route("/predict")
    class Predict(Resource):
        @ns_pred.expect(predict_request, validate=True)
        @ns_pred.response(200, "OK", predict_response)
        @ns_pred.response(400, "Bad Request", error_response)
        @ns_pred.response(500, "Internal Server Error", error_response)
        def post(self):
            payload = request.get_json(silent=True) or {}
            features = payload.get("features")

            try:
                features = validate_features(features)
            except ValueError as e:
                return {"error": str(e), "request_id": g.request_id}, 400

            try:
                pred, risk = predict_one(model, features)
            except Exception:
                logger.exception("Erro na inferência request_id=%s", g.request_id)
                return {"error": "Erro interno ao executar inferência.", "request_id": g.request_id}, 500

            return {
                "prediction": int(pred),
                "risk_score": float(risk),
                "model_version": MODEL_VERSION,
                "request_id": g.request_id,
            }, 200

    @ns_monitor.route("/monitoring")
    class Monitoring(Resource):
        @ns_monitor.response(200, "Drift Report HTML")
        @ns_monitor.response(404, "Relatório não encontrado", error_response)
        def get(self):
            BASE_DIR = Path(__file__).resolve().parent.parent
            report_path = BASE_DIR / "monitoring" / "drift_report.html"

            if report_path.exists():
                return send_file(str(report_path))
            else:
                return {
                    "error": "Drift report não encontrado. Gere o relatório primeiro.",
                    "request_id": g.request_id,
                }, 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)