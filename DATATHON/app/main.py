# app/main.py
from flask import Flask, request, jsonify
from app.model_runtime import load_model, predict_one, MODEL_VERSION

def create_app():
    app = Flask(__name__)
    model = load_model()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "model_version": MODEL_VERSION})

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or {}

        # contrato: {"features": {...}}
        features = payload.get("features")
        if not isinstance(features, dict):
            return jsonify({
                "error": "Formato inválido. Envie JSON no formato: {'features': {...}}"
            }), 400

        pred, risk = predict_one(model, features)
        return jsonify({
            "prediction": int(pred),
            "risk_score": float(risk),
            "model_version": MODEL_VERSION
        })

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
