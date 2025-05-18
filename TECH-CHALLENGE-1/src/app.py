# Author: Caique Nascimento e Gustavo Carrillo

# AJUSTAR E INCLUIR:

#   http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ProcessaViniferas.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ProcessaAmericanas.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ProcessaMesa.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ProcessaSemclass.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/Comercio.csv 
#   http://vitibrasil.cnpuv.embrapa.br/download/ImpVinhos.csv 
#   http://vitibrasil.cnpuv.embrapa.br/download/ImpEspumantes.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ImpFrescas.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ImpPassas.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ImpSuco.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ExpVinho.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ExpEspumantes.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ExpUva.csv
#   http://vitibrasil.cnpuv.embrapa.br/download/ExpSuco.csv



# Realizando os imports necessários
from flask import Flask, jsonify, request, render_template_string
from flask_restx import Api, Resource, fields
import pandas as pd
import requests
from io import StringIO

# Configurando o Flask e o Flask-RESTx
app = Flask(__name__)
api = Api(app, version='1.0', title='API Embrapa - Dados Vitivinícolas',
          description='Consulta dados públicos da Embrapa diretamente dos arquivos CSV por categoria')

ns = api.namespace('dados', description='Operações com os dados vitivinícolas')

# Mapeamento de categorias para URLs dos arquivos CSV
CSV_URLS = {
    'producao': 'http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv',
    'processa_viniferas': 'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaViniferas.csv',
    'processa_americanas': 'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaAmericanas.csv',
    'processa_mesa': 'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaMesa.csv',
    'processa_semclass': 'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaSemclass.csv',
    'comercio': 'http://vitibrasil.cnpuv.embrapa.br/download/Comercio.csv',
    'imp_vinhos': 'http://vitibrasil.cnpuv.embrapa.br/download/ImpVinhos.csv',
    'imp_espumantes': 'http://vitibrasil.cnpuv.embrapa.br/download/ImpEspumantes.csv',
    'imp_frescas': 'http://vitibrasil.cnpuv.embrapa.br/download/ImpFrescas.csv',
    'imp_passas': 'http://vitibrasil.cnpuv.embrapa.br/download/ImpPassas.csv',
    'imp_suco': 'http://vitibrasil.cnpuv.embrapa.br/download/ImpSuco.csv',
    'exp_vinho': 'http://vitibrasil.cnpuv.embrapa.br/download/ExpVinho.csv',
    'exp_espumantes': 'http://vitibrasil.cnpuv.embrapa.br/download/ExpEspumantes.csv',
    'exp_uva': 'http://vitibrasil.cnpuv.embrapa.br/download/ExpUva.csv',
    'exp_suco': 'http://vitibrasil.cnpuv.embrapa.br/download/ExpSuco.csv'
}

CSV_CONFIGS = {
    'producao': {'sep': ';', 'encoding': 'latin1'},
    'processa_viniferas': {'sep': ';', 'encoding': 'utf-8'},
    'processa_americanas': {'sep': ';', 'encoding': 'utf-8'},
    'processa_mesa': {'sep': ';', 'encoding': 'utf-8'},
    'processa_semclass': {'sep': ';', 'encoding': 'utf-8'},
    'comercio': {'sep': ';', 'encoding': 'latin1'},
    'imp_vinhos': {'sep': ' ', 'encoding': 'utf-8'},
    'imp_espumantes': {'sep': ';', 'encoding': 'utf-8'},
    'imp_frescas': {'sep': ';', 'encoding': 'utf-8'},
    'imp_passas': {'sep': ';', 'encoding': 'utf-8'},
    'imp_suco': {'sep': ';', 'encoding': 'utf-8'},
    'exp_vinho': {'sep': ';', 'encoding': 'utf-8'},
    'exp_espumantes': {'sep': ';', 'encoding': 'utf-8'},
    'exp_uva': {'sep': ';', 'encoding': 'utf-8'},
    'exp_suco': {'sep': ';', 'encoding': 'utf-8'}
}

# Modelo para documentação do Swagger
categoria_model = api.model('Categoria', {
    'categoria': fields.String(required=True, description='Categoria dos dados (ex: producao, comercio, imp_suco...)')
})

# Função para carregar os dados do CSV de uma categoria específica
def carregar_dados(categoria):
    url = CSV_URLS.get(categoria)
    config = CSV_CONFIGS.get(categoria, {'sep': ';', 'encoding': 'utf-8'})
    if not url:
        return None
    try:
        response = requests.get(url)
        response.encoding = config['encoding']
        content = response.text.replace('\x00', '')
        df = pd.read_csv(StringIO(content), sep=config['sep'], engine='python', on_bad_lines='skip')
        return df
    except Exception as e:
        print(f"Erro ao carregar dados de {categoria}: {e}")
        return None

@ns.route('/')
class TodasAsLinhas(Resource):
    @ns.doc(params={'categoria': 'Nome da categoria desejada'})
    def get(self):
        """Retorna todos os dados da categoria informada"""
        categorias = request.args.getlist('categoria')
        if not categorias:
            return {'erro': 'Nenhuma categoria informada'}, 400
        resultado = {}
        for cat in categorias:
            df = carregar_dados(cat)
            if df is not None and not df.empty:
                resultado[cat] = df.to_dict(orient='records')
            else:
                resultado[cat] = f"Erro ao carregar dados da categoria: {cat}"
        return jsonify(resultado)

@ns.route('/<string:categoria>/<int:linha>')
@ns.param('categoria', 'Nome da categoria desejada')
@ns.param('linha', 'Índice da linha desejada')
class LinhaEspecifica(Resource):
    def get(self, categoria, linha):
        """Retorna os dados de uma linha específica de uma categoria"""
        df = carregar_dados(categoria)
        if df is None or df.empty:
            return {'erro': 'Categoria inválida ou erro ao carregar dados'}, 404
        if linha < 0 or linha >= len(df):
            return {'erro': 'Índice fora do intervalo'}, 400
        return jsonify(df.iloc[linha].to_dict())

@app.route('/')
def index():
    html = '''
    <html>
    <head><title>API Embrapa</title></head>
    <body>
        <h1>API de dados vitivinícolas da Embrapa</h1>
        <p>Selecione uma ou mais categorias abaixo:</p>
        <form method="get" action="/dados/">
            {% for key in categorias %}
                <input type="checkbox" name="categoria" value="{{ key }}"> {{ key }}<br>
            {% endfor %}
            <input type="submit" value="Buscar Dados">
        </form>
        <p><a href="/swagger-ui/">Documentação Swagger</a></p>
    </body>
    </html>
    '''
    return render_template_string(html, categorias=CSV_URLS.keys())

if __name__ == '__main__':
    app.run(debug=True)

