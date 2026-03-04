
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

## Tipo de problema

O problema tratado é uma **classificação binária**.

| Classe | Significado |
|------|-------------|
| 0 | Aluno sem risco relevante |
| 1 | Aluno com risco de defasagem |

---

## Modelo utilizado

O modelo selecionado foi:

RandomForestClassifier

Motivações da escolha:

- Alta performance em dados tabulares
- Baixa necessidade de normalização
- Robustez contra overfitting
- Capacidade de capturar relações não lineares

---

## Pipeline de inferência

O modelo utilizado em produção está armazenado em:

artifacts/model.pkl

Esse arquivo contém o **modelo final serializado** que é carregado pela API durante a inicialização.

O carregamento do modelo ocorre em:

app/model_runtime.py

Função responsável:

load_model()

---

## Threshold de decisão

O modelo retorna uma probabilidade (`risk_score`).

A classificação final (`prediction`) é obtida aplicando um threshold otimizado durante o treinamento.

Esse valor é armazenado em:

artifacts/threshold_final.txt

---

## Versão do modelo

A versão atual do modelo é armazenada em:

artifacts/model_version.txt

Essa informação é retornada pela API em cada predição.

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
