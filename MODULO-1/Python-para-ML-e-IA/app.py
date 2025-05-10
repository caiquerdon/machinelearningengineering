# CRIANDO UM AMBIENTE VIRTUAL(VENV)


# 1- Instalar a venv: python -m venv venv
# 2- Acessar a venv: source ./venv/bin/Activate
# 3- Instalar o FLASK no meu venv: Conferir se esta no (venv)e dar o pip install flask
    # O Flask é um microframework para Python que permite criar aplicações web de forma simples e rápida.
    # Ele é leve e flexível, permitindo que você escolha as bibliotecas e ferramentas que deseja usar.
from flask import Flask, jsonify, request # Importando as bibliotecas necessárias do Flask

app = Flask(__name__) # Criando a instancia Flask

@app.route('/') # Definindo a rota raiz com o decorador
def home():
    return "Hello, flask it's me!" # Retorno da funcao 

items = [] # Criando uma lista vazia para armazenar os itens

@app.route('/items', methods=['GET']) # Definindo a rota /items com os métodos GET 
def get_items():
    return jsonify(items)

@app.route('/items', methods=['POST']) # Definindo a rota /items com os métodos POST
def create_item():
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201

if __name__ == '__main__':
    app.run(debug=True) # Facilitando os testes e mostrando erros no navegador

# CRUD é um acrônimo que representa as quatro operações básicas de persistência de dados em um banco de dados:
# C - CREATE
# R - READ
# U - UPDATE
# D - DELETE

# CRIANDO O GET
    # O método GET é usado para solicitar dados de um servidor. Ele é o método padrão usado pelos navegadores para solicitar páginas da web.
