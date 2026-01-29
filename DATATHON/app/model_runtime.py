# app/model_runtime.py
import os
from typing import Dict, Any, Tuple

MODEL_VERSION = os.getenv("MODEL_VERSION", "stub-v0")

class StubModel:
    """
    Modelo provisório para você começar a API sem depender do pipeline.
    Depois você troca por load_model() + predict() reais.
    """
    def predict_proba_one(self, x: Dict[str, Any]) -> float:
        # regra simples só para a API responder
        idade = _safe_float(x.get("idade"))
        faltas = _safe_float(x.get("faltas"))

        score = 0.15
        if idade is not None and idade >= 16:
            score += 0.25
        if faltas is not None and faltas >= 10:
            score += 0.35
        return max(0.0, min(1.0, score))

def _safe_float(v):
    try:
        if v is None:
            return None
        return float(v)
    except (TypeError, ValueError):
        return None

def load_model():
    """
    HOJE: retorna StubModel.
    DEPOIS: carregar artifacts/model.pkl ou joblib e retornar o pipeline treinado.
    """
    return StubModel()

def predict_one(model, features: Dict[str, Any], threshold: float = 0.5) -> Tuple[int, float]:
    risk = model.predict_proba_one(features)
    pred = 1 if risk >= threshold else 0
    return pred, risk
