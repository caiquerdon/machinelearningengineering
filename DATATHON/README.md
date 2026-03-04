
# Datathon — Machine Learning Engineering
## Associação Passos Mágicos

---

- Caique Rodrigues do Nascimento
- Gustavo Bortolami Carrillo

# 1. Visão Geral

Este projeto implementa uma solução completa de **Machine Learning Engineering** para identificar alunos com **risco de defasagem escolar**.

O objetivo é permitir que a organização **Associação Passos Mágicos** identifique precocemente estudantes que necessitam de maior apoio educacional.

A solução inclui:

- Pipeline completo de Machine Learning
- API de inferência em Flask
- Empacotamento com Docker
- Testes automatizados
- Monitoramento de Data Drift
- Dashboard de monitoramento

---

# 2. Problema de Negócio

A defasagem escolar ocorre quando um estudante apresenta desempenho significativamente inferior ao esperado para sua idade ou série.

Identificar precocemente alunos em risco permite:

- Intervenções pedagógicas direcionadas
- Redução de evasão escolar
- Melhor uso de recursos educacionais
- Acompanhamento individualizado de estudantes

---

# 3. Arquitetura da Solução

A solução segue uma arquitetura típica de **MLOps**.

Dataset → Preprocessing → Feature Engineering → RandomForest Model → Serialized Model (model.pkl) → Flask API → Docker → Monitoring

Componentes:

-   API Flask com Swagger (Flask-RESTX)
-   Versionamento de modelo
-   Threshold estratégico
-   Logging estruturado
-   Testes unitários (≥ 80% cobertura)
-   Dashboard de Drift com Evidently

---

# 4. Pipeline de Machine Learning

O pipeline de treinamento está localizado na pasta:

src/

Principais etapas:

| Etapa | Descrição |
|------|-----------|
| preprocessing.py | Limpeza e preparação dos dados |
| feature_engineering.py | Criação de variáveis derivadas |
| target.py | Definição da variável alvo |
| train.py | Treinamento do modelo |
| evaluate.py | Avaliação de performance |

---

# 5. Modelo de Machine Learning

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

# 6. API de Inferência

A API foi construída utilizando **Flask + Flask-RESTX**.

Endpoints principais:

| Endpoint | Descrição |
|--------|-----------|
| /health | Status da API |
| /predict | Executa inferência |
| /monitoring | Dashboard de drift |
| /docs | Swagger UI |

Swagger disponível em:

http://localhost:8000/docs

---

# 7. Exemplo de Predição

Request:

{
  "features": {
    "Idade": 17
  }
}

Resposta:

{
  "prediction": 0,
  "risk_score": 0.32,
  "model_version": "v1",
  "request_id": "..."
}

---

# 8. Monitoramento do Modelo

O projeto implementa **monitoramento de Data Drift** utilizando a biblioteca Evidently.

O monitoramento compara:

- dados históricos de treinamento
- dados recentes de produção

Para gerar o relatório:

python monitoring/generate_drift_report.py

O relatório será salvo em:

monitoring/drift_report.html

Também pode ser acessado via API:

http://localhost:8000/monitoring

---

# 9. Testes

Os testes estão localizados em:

tests/

Executar:

pytest

Cobertura de código:

pytest --cov

Cobertura alvo do projeto:

>= 80%

---

# 10. Docker

Build da imagem:

docker build -t datathon-ml .

Executar container:

docker run -p 8000:8000 datathon-ml

---

# 11. Estrutura do Projeto

    DATATHON/
    │
    ├── app/
    │   ├── main.py
    │   ├── model_runtime.py
    │   ├── validation.py  
    │
    ├── artifacts/
    │   ├── model.pkl
    │   ├── model_version.txt
    │   └── threshold_final.txt
    │
    ├── data/
    │   ├── base_datathon.xlsx
    │   └── predicoes_2024_com_classificacao.csv
    │
    ├── monitoring/
    │   ├── generate_drift_report.py
    │   └── drift_report.html
    │
    ├── tests/
    │   ├── test_api.py
    │   └── test_model_runtime.py
    │   └── test_preprocessing.py
    │   └── test_target.py
    │   └── test_validation.py
    │
    ├── Dockerfile
    ├── requirements.txt
    └── README.md

---
## 12. Executando o Projeto

### Pré-requisitos

-   Python 3.10+
-   Docker (opcional)

### Instalar dependências

``` bash
pip install -r requirements.txt
```

### Subir API

``` bash
python -m app.main
```

Swagger disponível em:

http://localhost:8000/docs

## 13. Próximos Passos

-   Automatizar geração de drift
-   Implementar re-treinamento automático
-   CI/CD para deploy contínuo
-   Monitoramento com Prometheus + Grafana
-   Deploy em Kubernetes

---
# 14. Conclusão

Este projeto implementa um **pipeline completo de Machine Learning Engineering**, incluindo:

-   Modelagem
-   API de inferência
-   Dockerização
-   Testes automatizados
-   Monitoramento contínuo
-   Dashboard de Drift
-   Versionamento de modelo

A solução está pronta para ambiente de produção e evolução contínua.
