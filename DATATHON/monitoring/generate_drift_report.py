from pathlib import Path
import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# ======================================
# 1. Definir diretório base do projeto
# ======================================

BASE_DIR = Path(__file__).resolve().parent.parent

reference_path = BASE_DIR / "data" / "base_datathon.xlsx"
current_path = BASE_DIR / "data" / "predicoes_2024_com_classificacao.csv"

print(f"Reference path: {reference_path}")
print(f"Current path: {current_path}")

# ======================================
# 2. Carregar dados
# ======================================

reference_data = pd.read_excel(reference_path)
current_data = pd.read_csv(current_path)

print("Reference shape:", reference_data.shape)
print("Current shape:", current_data.shape)

# ======================================
# 3. Remover colunas que NÃO são features
# ======================================

cols_to_drop = [
    "prediction",
    "risk_score",
    "classificacao",
    "target",
]

reference_data = reference_data.drop(columns=[c for c in cols_to_drop if c in reference_data.columns], errors="ignore")
current_data = current_data.drop(columns=[c for c in cols_to_drop if c in current_data.columns], errors="ignore")

# Manter apenas colunas em comum
common_columns = list(set(reference_data.columns) & set(current_data.columns))

reference_data = reference_data[common_columns]
current_data = current_data[common_columns]

print("Colunas em comum:", len(common_columns))

# ======================================
# 4. Corrigir tipos automaticamente
# ======================================

for col in common_columns:
    ref_numeric = pd.to_numeric(reference_data[col], errors="coerce")
    cur_numeric = pd.to_numeric(current_data[col], errors="coerce")

    # Se maioria dos valores for numérica → tratar como numérico
    if ref_numeric.notna().mean() > 0.5 and cur_numeric.notna().mean() > 0.5:
        reference_data[col] = ref_numeric.astype(float)
        current_data[col] = cur_numeric.astype(float)
    else:
        reference_data[col] = reference_data[col].astype(str)
        current_data[col] = current_data[col].astype(str)

# ======================================
# 5. Remover colunas vazias (crítico)
# ======================================

valid_columns = []

for col in reference_data.columns:
    if (
        reference_data[col].notna().sum() > 0
        and current_data[col].notna().sum() > 0
    ):
        valid_columns.append(col)

reference_data = reference_data[valid_columns]
current_data = current_data[valid_columns]

print("Colunas finais usadas no drift:", len(valid_columns))

# ======================================
# 6. Criar relatório de Drift
# ======================================

report = Report(metrics=[DataDriftPreset()])

report.run(
    reference_data=reference_data,
    current_data=current_data,
)

# ======================================
# 7. Salvar relatório HTML
# ======================================

output_path = BASE_DIR / "monitoring" / "drift_report.html"
report.save_html(str(output_path))

print("✅ Drift report gerado com sucesso!")
print(f"Arquivo salvo em: {output_path}")