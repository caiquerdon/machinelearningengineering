# app/main.py
from flask import Flask, request, jsonify

from app.model_runtime import load_model, predict_one, MODEL_VERSION
from app.validation import validate_features


def create_app():
    app = Flask(__name__)
    model = load_model()

    @app.get("/")
    def home():
        return jsonify({"message": "API no ar. Use /health e /predict"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "model_version": MODEL_VERSION})

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or {}

        # contrato: {"features": {...}}
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
