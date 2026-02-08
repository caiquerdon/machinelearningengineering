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

<img width="1259" height="943" alt="01_target_rate_train_vs_holdout" src="https://github.com/user-attachments/assets/2a293b29-7717-4f23-b59c-f495af8703e5" />

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
<img width="1259" height="942" alt="02_precision_recall_curve" src="https://github.com/user-attachments/assets/62ec68ab-bd86-4c8b-9224-3d4e49951e84" />
<img width="1259" height="942" alt="03_roc_curve" src="https://github.com/user-attachments/assets/5960a73d-0b26-45e0-b459-ddc960de10a5" />
<img width="1059" height="942" alt="04_confusion_matrix" src="https://github.com/user-attachments/assets/73eb479c-a256-4a99-97a7-7af5356fcdbe" />

---

## 🔎 Interpretabilidade

<img width="1652" height="1181" alt="06_feature_importance_top20" src="https://github.com/user-attachments/assets/ad6f53c1-96f8-4bc3-bdc5-9bfdb2409bd1" />

A feature mais importante (`num__def_bin`) representa histórico de defasagem escolar, construída sem vazamento de informação.

---

## 🚀 Produção

Artefatos gerados:
- Modelo treinado (`.pkl`)
- CSV com predições de 2024
- Threshold operacional fixo

---

📌 *Projeto desenvolvido para o Datathon – Pós Tech | Machine Learning & MLOps.*
