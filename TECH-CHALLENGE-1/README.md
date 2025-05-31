
# API Embrapa - Vitivinicultura

Este projeto faz parte do Tech Challenge da Pós-Graduação em Engenharia de Machine Learning.

## 📌 Objetivo

Criar uma API REST em Python que consome dados públicos do site da Embrapa (VitiBrasil) e os disponibiliza em formato JSON, com documentação automática via Swagger.

## 🚀 Funcionalidades

- Consulta dos dados da aba **Produção** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Processamento** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Comercialização** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Importação** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Exportação** diretamente do CSV oficial da Embrapa.
- API REST com Flask.
- Documentação via Swagger (Flask-RESTX).

## 🔧 Tecnologias

- Python 3.9+
- Flask
- Flask-RESTX
- Pandas
- Requests

## 📂 Endpoints

### `GET /producao/`

Retorna todos os dados da aba Produção da Embrapa.

### `GET /producao/<linha>`

Retorna uma linha específica pelo índice (inteiro).

### `GET /`

Mensagem de boas-vindas e link para a documentação.

## 📄 Documentação Swagger

Disponível automaticamente em:

```
https://api-embrapa-28xn.onrender.com
```

## ▶️ Como executar localmente

1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/tech-challenge-embrapa.git
cd tech-challenge-embrapa
```

2. Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute o app:

```bash
python app.py
```

## 🔐 Segurança

A API atualmente está pública. Para produção, recomenda-se o uso de autenticação via JWT ou chave de API.

## 🧠 Possível uso em ML

Os dados obtidos por essa API podem ser usados para:
- Previsão de produção por estado ou tipo de uva
- Análise de sazonalidade
- Estudos de exportação/importação de vinho

## 📌 Desafio proposto

Este projeto é parte do desafio da Fase 1 da Pós-Graduação em Engenharia de Machine Learning e representa 60% da nota da fase.

## 🧑‍💻 Autores

Caique Nascimento
Gustavo Carrillo
