# tests/test_validation.py
import pytest

def test_validate_features_ok():
    from app.validation import validate_features
    out = validate_features({"a": 1})
    assert out["a"] == 1

def test_validate_features_not_dict():
    from app.validation import validate_features
    with pytest.raises(ValueError):
        validate_features(["a", 1])

def test_validate_features_empty():
    from app.validation import validate_features
    with pytest.raises(ValueError):
        validate_features({})
