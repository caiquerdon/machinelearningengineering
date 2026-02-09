# app/model_runtime.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple, List
import os

import numpy as np
import pandas as pd
import joblib

PROJECT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"

MODEL_PATH = Path(os.getenv("MODEL_PATH", str(ARTIFACTS_DIR / "model.pkl")))
THRESHOLD_PATH = Path(os.getenv("THRESHOLD_PATH", str(ARTIFACTS_DIR / "threshold_final.txt")))
MODEL_VERSION_PATH = Path(os.getenv("MODEL_VERSION_PATH", str(ARTIFACTS_DIR / "model_version.txt")))


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return None


MODEL_VERSION = os.getenv("MODEL_VERSION") or _read_text(MODEL_VERSION_PATH) or "unknown"


def _read_threshold(path: Path) -> float:
    env_thr = os.getenv("THRESHOLD")
    if env_thr:
        return float(env_thr)

    txt = _read_text(path)
    if not txt:
        return 0.5
    return float(txt)


THRESHOLD = _read_threshold(THRESHOLD_PATH)


def load_model() -> Any:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo não encontrado em: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def _expected_columns(model: Any) -> List[str]:
    """
    Tenta descobrir as colunas esperadas pelo pipeline.
    - Em geral, Pipelines/ColumnTransformers expõem feature_names_in_ após fit.
    """
    if hasattr(model, "feature_names_in_"):
        return list(getattr(model, "feature_names_in_"))

    # fallback comum: pipeline com preprocessor interno
    if hasattr(model, "named_steps"):
        for step in model.named_steps.values():
            if hasattr(step, "feature_names_in_"):
                return list(getattr(step, "feature_names_in_"))

    return []


def _normalize_key(s: str) -> str:
    return s.strip().lower()


def _to_dataframe_with_schema(model: Any, features: Dict[str, Any]) -> pd.DataFrame:
    """
    Cria DF com todas colunas esperadas pelo modelo (preenchidas com NaN),
    e seta as features enviadas no payload.
    Faz match case-insensitive para chaves (idade -> Idade).
    """
    expected = _expected_columns(model)

    if expected:
        X = pd.DataFrame([{c: np.nan for c in expected}])

        # map normalizado -> nome real esperado
        norm_map = {_normalize_key(c): c for c in expected}

        for k, v in features.items():
            if not isinstance(k, str):
                continue
            nk = _normalize_key(k)
            real_col = norm_map.get(nk, k)  # se não achar, tenta usar como veio
            if real_col in X.columns:
                X.at[0, real_col] = v
            else:
                # se vier coluna extra, adiciona (não atrapalha o ColumnTransformer,
                # porque ele seleciona por nome as colunas que conhece)
                X[real_col] = np.nan
                X.at[0, real_col] = v
        return X

    # se não conseguimos inferir o schema, usa o que vier
    return pd.DataFrame([features])


def _get_positive_class_probability(model: Any, X: pd.DataFrame) -> float:
    if not hasattr(model, "predict_proba"):
        pred = model.predict(X)
        return float(pred[0])

    proba = model.predict_proba(X)
    proba = np.asarray(proba)

    if hasattr(model, "classes_"):
        classes = list(getattr(model, "classes_"))
        if 1 in classes:
            idx = classes.index(1)
            return float(proba[0, idx])

    if proba.ndim == 2 and proba.shape[1] >= 2:
        return float(proba[0, 1])

    return float(np.ravel(proba)[0])


def predict_one(model: Any, features: Dict[str, Any]) -> Tuple[int, float]:
    X = _to_dataframe_with_schema(model, features)
    risk = _get_positive_class_probability(model, X)
    pred = 1 if risk >= THRESHOLD else 0
    return int(pred), float(risk)
