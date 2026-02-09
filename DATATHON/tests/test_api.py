# tests/test_api.py

def test_health_ok():
    from app.main import create_app

    app = create_app()
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "ok"
    assert "model_version" in data


def test_predict_ok_with_valid_payload():
    from app.main import create_app

    app = create_app()
    client = app.test_client()

    payload = {"features": {"Idade": 17}}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200

    data = resp.get_json()
    assert "prediction" in data
    assert "risk_score" in data
    assert "model_version" in data

    assert isinstance(data["prediction"], int)
    assert isinstance(data["risk_score"], (int, float))
    assert 0.0 <= float(data["risk_score"]) <= 1.0


def test_predict_400_when_no_json_body():
    from app.main import create_app

    app = create_app()
    client = app.test_client()

    resp = client.post("/predict")  # sem body
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_predict_400_when_features_missing():
    from app.main import create_app

    app = create_app()
    client = app.test_client()

    resp = client.post("/predict", json={"x": 1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_predict_400_when_features_not_dict():
    from app.main import create_app

    app = create_app()
    client = app.test_client()

    resp = client.post("/predict", json={"features": ["idade", 17]})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_predict_400_when_features_empty_dict():
    from app.main import create_app

    app = create_app()
    client = app.test_client()

    resp = client.post("/predict", json={"features": {}})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
