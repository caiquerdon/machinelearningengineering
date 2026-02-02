# tests/test_target.py
import pandas as pd
import pytest

def test_build_target_threshold_2():
    from src.target import build_target_defasagem

    df = pd.DataFrame({"defasagem": [-2, -1, 0, 1, 2, 3]})
    y = build_target_defasagem(df, threshold=2).tolist()
    assert y == [0, 0, 0, 0, 1, 1]

def test_build_target_threshold_1():
    from src.target import build_target_defasagem

    df = pd.DataFrame({"defasagem": [-1, 0, 1, 2]})
    y = build_target_defasagem(df, threshold=1).tolist()
    assert y == [0, 0, 1, 1]

def test_build_target_missing_column():
    from src.target import build_target_defasagem

    df = pd.DataFrame({"x": [1, 2, 3]})
    with pytest.raises(ValueError):
        build_target_defasagem(df)
