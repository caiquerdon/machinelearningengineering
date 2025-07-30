# Projeto AWS Glue ETL - B3 Pregão Diário (IBOV)

Este projeto foi desenvolvido como parte da pós-graduação em Engenharia de Machine Learning – FIAP. Ele automatiza a ingestão, o armazenamento e o processamento da carteira do índice IBOVESPA (IBOV) utilizando serviços da AWS.

## Arquitetura

```
[B3 URL - CSV em base64]
      ↓
[Glue Scapperb3 - Download + upload parquet no S3 particionado]
      ↓ (PUT)
[S3 Bucket (por data: year/month/day)]
      ↓ (Evento PUT)
[Lambda  - Trigger do Glue Job visual]
      ↓
[Glue ETL Job Visual - Transformação e output]
```

## Serviços AWS Utilizados

|     Serviço     |                             Função                                     |
|-----------------|------------------------------------------------------------------------|
| Glue Scraper B3 |         Faz download e salva em S3 como Parquet                        |
|        S3       |         Armazenamento de dados particionados (year/month/day)          |
|     Glue Job    |         ETL Visual criado via Glue Studio                              |

## Como funciona

1. **GLUE SCRAPER B3 (`scraper-b3.py`)**: Faz requisição à URL da B3, decodifica o conteúdo base64 e salva como arquivo `.parquet` no S3 em um caminho particionado por data.

2. **S3 Bucket**: `s3://b3-dados-pregao-fiap-2025/b3/index=IBOV/year=YYYY/month=MM/day=DD/output.parquet`

3. **Lambda-b3-trigger-glue.py (`lambda-b3-trigger-glue`)**: É acionada automaticamente por evento PUT no bucket e dispara o Glue Job visual (`Glue_B3`).
4. **Glue Job Visual**: Lê dados do S3, processa e grava novos outputs prontos para análise.

## 🔍 Consulta com Athena (opcional)

```sql
SELECT * FROM b3_carteira_ibov
WHERE year = '2025' AND month = '07' AND day = '30';
```

## Estrutura de diretório no S3

```
s3://b3-dados-pregao-fiap-2025/
└── b3/
    └── index=IBOV/
        └── year=2025/
            └── month=07/
                └── day=30/
                    └── output.parquet
```

## Autor
Caique Rodrigues do Nascimento
Gustavo Bortolami Carrillo
