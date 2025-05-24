
from flask import Flask, jsonify, request, render_template_string
from flask_restx import Api, Resource, fields
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "bagre123"  # Trocar em produção!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

api = Api(app, version='1.0', title='API Embrapa - Dados Vitivinícolas',
          description='Consulta dados públicos da Embrapa diretamente dos arquivos CSV por categoria')

ns = api.namespace('dados', description='Operações com os dados vitivinícolas')

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
    'exp_suco': 'http://vitibrasil.cnpuv.embrapa.br/download/ExpSuco.csv',
}

CSV_CONFIGS = {
    'producao': {'sep': ';', 'encoding': 'latin1'},
    'processa_viniferas': {'sep': ';', 'encoding': 'latin1'},
    'processa_americanas': {'sep': '\t', 'encoding': 'latin1'},
    'processa_mesa': {'sep': '\t', 'encoding': 'latin1'},
    'processa_semclass': {'sep': '\t', 'encoding': 'latin1'},
    'comercio': {'sep': ';', 'encoding': 'latin1'},
    'imp_vinhos': {'sep': '\t', 'encoding': 'latin1'},
    'imp_espumantes': {'sep': '\t', 'encoding': 'latin1'},
    'imp_frescas': {'sep': '\t', 'encoding': 'latin1'},
    'imp_passas': {'sep': '\t', 'encoding': 'latin1'},
    'imp_suco': {'sep': ';', 'encoding': 'latin1'},
    'exp_vinho': {'sep': r'\s{1,}', 'encoding': 'latin1'},
    'exp_espumantes': {'sep': r'\s{1,}', 'encoding': 'latin1'},
    'exp_uva': {'sep': r'\s{1,}', 'encoding': 'latin1'},
    'exp_suco': {'sep': r'\s{1,}', 'encoding': 'latin1'},
}

def carregar_dados(categoria):
    url = CSV_URLS.get(categoria)
    config = CSV_CONFIGS.get(categoria, {'sep': ';', 'encoding': 'utf-8'})
    if not url:
        return None
    try:
        response = requests.get(url, timeout=10)
        response.encoding = config['encoding']
        content = response.text.replace('\x00', '').strip()
        df = pd.read_csv(
            StringIO(content),
            sep=config['sep'],
            engine='python',
            on_bad_lines='skip',
            skip_blank_lines=True
        )
        if len(df.columns) > 1 and not df.empty:
            df.dropna(how='all', inplace=True)
            df.columns = [str(col).strip() for col in df.columns]
            return df
    except Exception as e:
        print(f"[{categoria}] Erro ao carregar CSV: {e}")
    return None

@api.route('/login')
class Login(Resource):
    @api.doc(params={'username': 'Usuário', 'password': 'Senha'})
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        if username == 'admin' and password == '123':
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
        return {'erro': 'Credenciais inválidas'}, 401

@api.route('/categorias')
class ListaCategorias(Resource):
    @api.doc(description="Lista todas as categorias de dados vitivinícolas disponíveis")
    def get(self):
        return jsonify({
            "categorias_disponiveis": list(CSV_URLS.keys())
        })

@ns.route('/')
class TodasAsLinhas(Resource):
    @jwt_required()
    @ns.doc(params={'categoria': 'Nome da categoria desejada (pode repetir ?categoria=...)'})
    def get(self):
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
    @jwt_required()
    def get(self, categoria, linha):
        df = carregar_dados(categoria)
        if df is None or df.empty:
            return {'erro': 'Categoria inválida ou erro ao carregar dados'}, 404
        if linha < 0 or linha >= len(df):
            return {'erro': 'Índice fora do intervalo'}, 400
        return jsonify(df.iloc[linha].to_dict())

@app.route('/')
def index():
    return "API Embrapa com JWT protegida. Acesse /swagger-ui/ para documentação."

if __name__ == '__main__':
    app.run(debug=True)
