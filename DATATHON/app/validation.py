# app/validation.py
from typing import Any, Dict

def validate_features(features: Any) -> Dict[str, Any]:
    if not isinstance(features, dict):
        raise ValueError("Campo 'features' deve ser um dicionário.")
    if len(features) == 0:
        raise ValueError("Campo 'features' não pode ser vazio.")
    return features
