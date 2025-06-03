# API Embrapa – Dados Vitivinícolas

Esta aplicação disponibiliza uma API pública para consulta dos dados vitivinícolas da Embrapa, incluindo produção nacional, importações e exportações de uvas, vinhos, sucos e derivados.

## 🔗 Acesse a API
Acesse a API e sua documentação interativa hospedada gratuitamente no Render:

👉 https://api-embrapa-28xn.onrender.com

## ▶️ Vídeo demonstrativo do Deploy : 
https://www.youtube.com/watch?v=AEXQBhZ0rB0&feature=youtu.be

---

## Arqueitetura do projeto

![Arquitetura do Projeto](images/Arquitetura-TechChalange1.png

## 🛠 Tecnologias Utilizadas

- **Python 3.9 ou superior+**
- **Flask**
- **Flask-RESTx**
- **Pandas**
- **Requests**
- **Gunicorn** (para deploy no Render)

---

## 📌 Funcionalidades da API

- Consulta dos dados da aba **Produção** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Processamento** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Comercialização** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Importação** diretamente do CSV oficial da Embrapa.
- Consulta dos dados da aba **Exportação** diretamente do CSV oficial da Embrapa.
- API REST construída com **Flask** e documentada com **Flask-RESTX**.
- Retorno em formato JSON e interface interativa via Swagger UI.

---

### 🔹 Listar Categorias
```
GET /categorias
```

### 🔹 Obter todos os dados de uma categoria
```
GET /dados/categoria/<categoria>
```

## 📄 Exemplo de Retorno

### Exemplo `/dados/categoria/producao`
```json
[
  {
    "Ano": 2020,
    "Região": "Serra Gaúcha",
    "Quantidade (t)": 123456
  }
]
```

---

## 🖥️ Página Inicial

A rota `/` exibe uma página HTML simples e links diretos para as categorias, além do link para a documentação Swagger.

---

## 🚀 Deploy no Render

### Estrutura esperada:
```
.
├── app.py
├── requirements.txt
└── Procfile
```

### Exemplo de `Procfile` 
```txt
web: gunicorn app:app
```

---

## ▶️ Como Executar Localmente

### 1. Clone o repositório:

```bash
git clone https://github.com/caiquerdon/machinelearningengineering.git
cd TECH-CHALLENGE-1
```

### 2. (Opcional) Crie um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências:

```bash
cd src
pip install -r requirements.txt
```

### 4. Execute a aplicação:

```bash
python app.py
```

Acesse http://localhost:5000 no navegador.

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
## 👨‍💻 Autores

- **Caique Nascimento**
- **Gustavo Carrillo**