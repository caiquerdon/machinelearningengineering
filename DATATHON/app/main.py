# app/main.py
import time
import uuid
import logging
from flask import Flask, request, jsonify, g

from app.model_runtime import load_model, predict_one, MODEL_VERSION
from app.validation import validate_features


def create_app():
    app = Flask(__name__)
    model = load_model()

    # Logging para console (ideal para Docker)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logger = logging.getLogger("datathon-api")

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

        # devolve o request id para facilitar debug
        response.headers["X-Request-Id"] = getattr(g, "request_id", "-")
        return response

    @app.get("/")
    def home():
        return jsonify({"message": "API no ar. Use /health e /predict"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "model_version": MODEL_VERSION})

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or {}

        features = payload.get("features")
        try:
            features = validate_features(features)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        pred, risk = predict_one(model, features)
        return jsonify(
            {
                "prediction": int(pred),
                "risk_score": float(risk),
                "model_version": MODEL_VERSION,
            }
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

