# tests/test_model_runtime.py
def test_predict_one_returns_types_and_range():
    from app.model_runtime import load_model, predict_one

    model = load_model()
    pred, risk = predict_one(model, {"idade": 17, "faltas": 12})

    assert isinstance(pred, int)
    assert isinstance(risk, float)
    assert 0.0 <= risk <= 1.0
