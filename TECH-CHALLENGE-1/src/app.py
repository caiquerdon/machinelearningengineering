# Author: Caique Nascimento e Gustavo Carrillo

# Realizando os imports necessários
from flask import Flask, jsonify
from flask_restx import Api, Resource
import pandas as pd
import requests
from io import StringIO

# Configurando o Flask e o Flask-RESTx
app = Flask(__name__)
api = Api(app, version='1.0', title='API Embrapa - Produção',
          description='Consulta os dados de produção vitivinícola da Embrapa diretamente do CSV oficial')
ns = api.namespace('producao', description='Operações com os dados de produção')

# URL do CSV
# Definindo a URL do CSV e os parâmetros de leitura
# O CSV contém dados de produção vitivinícola
CSV_URL = 'http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv'
CSV_SEP = ';'
CSV_ENCODING = 'latin1'

# Função para carregar os dados do CSV
def carregar_dados():
    response = requests.get(CSV_URL)
    response.encoding = CSV_ENCODING
    df = pd.read_csv(StringIO(response.text), sep=CSV_SEP)
    return df
@ns.route('/')

class TodasAsLinhas(Resource):
    @ns.doc('listar_todas_linhas')
    def get(self):
        """Retorna todos os dados de produção"""
        df = carregar_dados()
        return jsonify(df.to_dict(orient='records'))

@ns.route('/<int:linha>')
@ns.param('linha', 'O índice da linha desejada')
class LinhaEspecifica(Resource):
    @ns.doc('obter_linha_especifica')
    def get(self, linha):
        """Retorna os dados de uma linha específica pela posição do índice"""
        df = carregar_dados()
        if linha < 0 or linha >= len(df):
            return {'erro': 'Índice fora do intervalo'}, 404
        return jsonify(df.iloc[linha].to_dict())

@app.route('/')
def index():
    return jsonify({
        "mensagem": "API de Produção da Embrapa disponível em /producao",
        "documentacao": "/swagger-ui/"
    })

if __name__ == '__main__':
    app.run(debug=True)
