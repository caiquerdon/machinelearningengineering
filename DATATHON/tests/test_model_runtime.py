# tests/test_model_runtime.py

from app.model_runtime import load_model, predict_one


def test_predict_one_returns_types_and_range():
    model = load_model()

    assert model is not None

    pred, risk = predict_one(model, {"Idade": 17})

    # tipos
    assert isinstance(pred, int)
    assert isinstance(risk, float)

    # intervalo esperado
    assert pred in (0, 1)
    assert 0.0 <= risk <= 1.0