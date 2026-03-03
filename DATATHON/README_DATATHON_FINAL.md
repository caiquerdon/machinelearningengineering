# 📊 Datathon --- Machine Learning Engineering

## Associação Passos Mágicos

------------------------------------------------------------------------

## 1. Visão Geral do Projeto

Este projeto desenvolve um modelo preditivo para estimar o risco de
defasagem escolar de estudantes atendidos pela Associação Passos
Mágicos.

A solução permite identificar alunos com maior risco educacional e
direcionar intervenções pedagógicas e psicossociais de forma
estratégica.

------------------------------------------------------------------------

## 2. Problema de Negócio

A defasagem escolar ocorre quando o estudante apresenta atraso no
aprendizado ou desempenho abaixo do esperado.

Identificar precocemente alunos em risco permite:

-   Direcionar apoio educacional personalizado
-   Reduzir evasão
-   Melhorar indicadores acadêmicos
-   Otimizar recursos institucionais

------------------------------------------------------------------------

## 3. Estratégia de Modelagem

### Tipo de Problema

Classificação binária:

-   0 → Sem risco relevante\
-   1 → Em risco de defasagem

### Modelo Utilizado

RandomForestClassifier

Selecionado por:

-   Robustez
-   Boa performance
-   Baixo risco de overfitting
-   Interpretabilidade

------------------------------------------------------------------------

## 4. Métricas

### Métrica Principal

**Recall da classe de risco**

Justificativa: em contexto social, é mais crítico não identificar um
aluno em risco (falso negativo) do que gerar falso positivo.

Métricas complementares:

-   F1-Score
-   ROC-AUC
-   Matriz de Confusão

------------------------------------------------------------------------

## 5. Arquitetura da Solução

Treinamento → Serialização → API Flask → Docker → Monitoramento →
Dashboard de Drift

Componentes:

-   API Flask com Swagger (Flask-RESTX)
-   Versionamento de modelo
-   Threshold estratégico
-   Logging estruturado
-   Testes unitários (≥ 80% cobertura)
-   Dashboard de Drift com Evidently

------------------------------------------------------------------------

## 6. Estrutura do Projeto

    DATATHON/
    │
    ├── app/
    │   ├── main.py
    │   ├── model_runtime.py
    │   ├── validation.py
    │
    ├── artifacts/
    │   ├── model_RandomForest.pkl
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
    │
    ├── Dockerfile
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 7. Executando o Projeto

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

------------------------------------------------------------------------

## 8. Endpoints

### GET /health

Retorna status da API e versão do modelo.

### POST /predict

Executa inferência.

Entrada:

``` json
{
  "features": {
    "Idade": 17
  }
}
```

### GET /monitoring

Retorna dashboard HTML de Data Drift.

------------------------------------------------------------------------

## 9. Monitoramento de Drift

O monitoramento compara:

-   Dados históricos de treino
-   Dados recentes de produção

Para gerar o relatório:

``` bash
python monitoring/generate_drift_report.py
```

O relatório é salvo em:

monitoring/drift_report.html

Também pode ser acessado via:

http://localhost:8000/monitoring

### Interpretação

No experimento atual, foi detectado drift em 100% das colunas
analisadas, indicando mudança significativa no perfil dos dados
recentes.

Esse resultado sugere necessidade potencial de reavaliação e possível
re-treinamento do modelo.

------------------------------------------------------------------------

## 10. Testes

``` bash
pytest
pytest --cov=app
```

Cobertura mínima garantida: ≥ 80%

------------------------------------------------------------------------

## 11. Docker

### Build

``` bash
docker build -t datathon-ml .
```

### Run

``` bash
docker run -p 8000:8000 datathon-ml
```

------------------------------------------------------------------------

## 12. Versionamento

Controlado via:

artifacts/model_version.txt

------------------------------------------------------------------------

## 13. Próximos Passos

-   Automatizar geração de drift
-   Implementar re-treinamento automático
-   CI/CD para deploy contínuo
-   Monitoramento com Prometheus + Grafana
-   Deploy em Kubernetes

------------------------------------------------------------------------

## 14. Conclusão

O projeto implementa o ciclo completo de Machine Learning Engineering:

-   Modelagem
-   API de inferência
-   Dockerização
-   Testes automatizados
-   Monitoramento contínuo
-   Dashboard de Drift
-   Versionamento de modelo

A solução está pronta para ambiente de produção e evolução contínua.
