# API Embrapa - Vitivinicultura

Este projeto faz parte do Tech Challenge da Pós-Graduação em Engenharia de Machine Learning.

---

## 📌 Objetivo

Criar uma API REST em Python que consome dados públicos do site da Embrapa (VitiBrasil) e os disponibiliza em formato JSON, com documentação automática via Swagger.

---

## 🚀 Funcionalidades

- Consulta dos dados da aba **Produção** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Processamento** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Comercialização** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Importação** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Exportação** diretamente do CSV oficial da Embrapa.
- API REST construída com **Flask** e documentada com **Flask-RESTX**.
- Retorno em formato JSON e interface interativa via Swagger UI.

---

## 🔧 Tecnologias Utilizadas

- Python 3.9+
- Flask
- Flask-RESTX
- Pandas
- Requests

---

## 🔗 Link da API em Produção

Acesse a API e sua documentação interativa hospedada gratuitamente no Render:

👉 https://api-embrapa-28xn.onrender.com

---

## 📂 Endpoints Principais

```
GET /                    → Mensagem de boas-vindas com link para documentação
GET /producao/           → Lista completa da aba Produção
GET /producao/<linha>    → Retorna uma linha específica por índice
# (Outros endpoints seguem padrão similar)
```

---

## 📄 Documentação Swagger

A interface Swagger é gerada automaticamente por meio do Flask-RESTX e está disponível em:

📍 https://api-embrapa-28xn.onrender.com

---

## ▶️ Como Executar Localmente

### 1. Clone o repositório:

```bash
git clone https://github.com/seuusuario/tech-challenge-embrapa.git
cd tech-challenge-embrapa
```

### 2. (Opcional) Crie um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação:

```bash
python app.py
```

Acesse http://localhost:5000/swagger-ui/ no navegador.

---

## 📁 Estrutura de Diretórios

```
.
├── app.py                  # Código principal da API
├── requirements.txt        # Dependências do projeto
├── Procfile                # Arquivo de execução para o Render
├── README.md               # Este arquivo :)
└── src/                    # Scripts e utilitários adicionais
```

---

## ⚙️ Sobre o Procfile

O `Procfile` é um arquivo usado por plataformas como o Render para saber como iniciar a aplicação. No nosso caso, ele contém:

```txt
web: gunicorn app:app
```

Isso instrui o Render a utilizar o Gunicorn para rodar a aplicação Flask a partir do arquivo `app.py`.

---

## 🔐 Segurança

Atualmente, a API está pública. Para ambientes de produção, recomenda-se implementar autenticação via JWT, OAuth2 ou chaves de API.

---

## 🤖 Possíveis Aplicações em Machine Learning

Os dados disponibilizados pela API podem servir como base para diversos estudos e modelos preditivos, como:

- Previsão de produção por estado ou tipo de uva
- Análise temporal e sazonalidade da produção
- Estudos de mercado para exportação/importação de vinhos

---

## 🎯 Desafio Acadêmico

Este projeto integra a **Fase 1** da Pós-Graduação em Engenharia de Machine Learning e compõe **60% da nota final** dessa etapa.

---

## 👨‍💻 Autores

- Caique Nascimento  
- Gustavo Carrillo
