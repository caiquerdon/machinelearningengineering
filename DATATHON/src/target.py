# src/target.py
import pandas as pd

def build_target_defasagem(df: pd.DataFrame, threshold: int = 2) -> pd.Series:
    """
    y=1 se defasagem >= threshold (atraso), senão 0.
    Negativos e 0 entram como 0.
    """
    if "defasagem" not in df.columns:
        raise ValueError("Coluna 'defasagem' não encontrada no dataframe.")
    return (df["defasagem"] >= threshold).astype(int)
