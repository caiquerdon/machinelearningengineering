# 📚 Datathon – Passos Mágicos  
## Predição de Risco de Defasagem Escolar

### Autor  
**Gustavo B. Carrillo**

---

## 🎯 Objetivo do Projeto

Desenvolver um modelo de Machine Learning capaz de **estimar o risco de defasagem escolar** de alunos atendidos pela Associação Passos Mágicos, permitindo **ações pedagógicas preventivas**, priorização de recursos e acompanhamento mais eficiente de alunos em situação de vulnerabilidade educacional.

O projeto contempla **todo o ciclo de vida do modelo**, desde análise exploratória até exportação de artefatos para uso em produção, seguindo boas práticas de MLOps.

---

## 🧠 Formulação do Problema

- **Tipo:** Classificação binária  
- **Target:** `Defasagem > 0`  
- **Classe positiva:** Alunos com risco de defasagem escolar  
- **Validação temporal (realista):**
  - Treino: **2022 + 2023**
  - Teste (holdout): **2024**

---

## 🔍 Análise Exploratória (EDA)

Foram realizadas as seguintes análises na base de treino (`df_train`):

- Análise de volumetria (linhas, colunas, alunos únicos)
- Remoção de colunas 100% nulas
- Verificação de inconsistências
- Análise de outliers
- Análise de data drift entre treino e teste

![Distribuição do target](imgs/01_target_rate_train_vs_holdout.png)

---

## 🏗️ Preparação de Dados

Pipeline com `ColumnTransformer`, garantindo reprodutibilidade e evitando data leakage.

---

## 🌲 Modelo Final: Random Forest

### Hiperparâmetros finais

```python
RandomForestClassifier(
    n_estimators=500,
    max_depth=8,
    min_samples_leaf=4,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)
```

### Justificativa
Os hiperparâmetros foram escolhidos visando reduzir overfitting, lidar com desbalanceamento e garantir boa generalização temporal.

---

## 📐 Estratégia de Threshold

Foi adotada a faixa:

```
0.60 ≤ Recall < 0.80
```

Essa faixa apresentou o melhor trade-off entre **recall** e **precision**, maximizando o F1-score e alinhando-se ao impacto educacional do problema.

---

## 📊 Avaliação

![PR Curve](imgs/02_precision_recall_curve.png)
![ROC Curve](imgs/03_roc_curve.png)
![Confusion Matrix](imgs/04_confusion_matrix.png)

---

## 🔎 Interpretabilidade

![Feature Importance](imgs/06_feature_importance_top20.png)

A feature mais importante (`num__def_bin`) representa histórico de defasagem escolar, construída sem vazamento de informação.

---

## 🚀 Produção

Artefatos gerados:
- Modelo treinado (`.pkl`)
- CSV com predições de 2024
- Threshold operacional fixo

---

📌 *Projeto desenvolvido para o Datathon – Pós Tech | Machine Learning & MLOps.*
