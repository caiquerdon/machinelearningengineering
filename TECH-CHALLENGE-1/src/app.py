##########################################
##############  Authors ##################
## Caique Nascimento e Gustavo Carrillo ##                                   
##########################################
##########################################



# Importando as bibliotecas necessárias
from flask import Flask, jsonify, request, render_template_string
from flask_restx import Api, Resource, fields
import pandas as pd
import requests
from io import StringIO

# Configuração do Flask
app = Flask(__name__)
api = Api(app, version='1.0', title='API Embrapa - Dados Vitivinícolas',
          description='Consulta dados públicos da Embrapa diretamente dos arquivos CSV por categoria')

# Configuração do namespace da API
ns = api.namespace('dados', description='Operações com os dados vitivinícolas')

# CSV 
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

# 
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

# 
categoria_model = api.model('Categoria', {
    'categoria': fields.String(required=True, description='Categoria dos dados')
})

# Funcao para carregar os dados de uma categoria específica
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
# Configuração do endpoint para obter todas as linhas de uma ou mais categorias
@ns.route('/')
# @ns.param('categoria', 'Nome da categoria desejada (pode repetir ?categoria=...)')
class TodasAsLinhas(Resource):
    @ns.doc(params={'categoria': 'Nome da categoria desejada (pode repetir ?categoria=...)'})
    def get(self):
        """Retorna todos os dados das categorias informadas"""
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

# Configuração do endpoint para obter uma linha específica de uma categoria
@ns.route('/<string:categoria>/<int:linha>')
@ns.param('categoria', 'Nome da categoria desejada')
@ns.param('linha', 'Índice da linha desejada')
class LinhaEspecifica(Resource):
    def get(self, categoria, linha):
        """Retorna os dados de uma linha específica"""
        df = carregar_dados(categoria)
        if df is None or df.empty:
            return {'erro': 'Categoria inválida ou erro ao carregar dados'}, 404
        if linha < 0 or linha >= len(df):
            return {'erro': 'Índice fora do intervalo'}, 400
        return jsonify(df.iloc[linha].to_dict())
    
# Configuração do endpoint para listar todas as categorias disponíveis
@api.route('/categorias')
class ListaCategorias(Resource):
    @api.doc(description="Lista todas as categorias de dados vitivinícolas disponíveis")
    def get(self):
        return jsonify({
            "categorias_disponiveis": list(CSV_URLS.keys())
        })
# Configuração do endpoint para acessar a documentação Swagger UI


@app.route('/')
def index():
     html = '''
     <html>
     <head>
         <title>API Embrapa</title>
         <style>
             body { font-family: Arial, sans-serif; display: flex; margin: 0; }
             .sidebar {
                 width: 250px;
                 background: #f2f2f2;
                 padding: 20px;
                 height: 100vh;
                 box-shadow: 2px 0px 5px rgba(0,0,0,0.1);
             }
             .content {
                 padding: 20px;
                 flex: 1;
             }
             .sidebar h2 {
                 margin-top: 0;
             }
             .categoria-link {
                 display: block;
                 margin: 8px 0;
                 color: #0066cc;
                 text-decoration: none;
             }
             .categoria-link:hover {
                 text-decoration: underline;
             }
         </style>
     </head>
     <body>
         <div class="sidebar">
             <h2>Categorias</h2>
             {% for key in categorias %}
                 <a class="categoria-link" href="/dados/?categoria={{ key }}">{{ key }}</a>
             {% endfor %}
             <br>
             <a href="/swagger-ui/">Documentação Swagger</a>
         </div>
         <div class="content">
             <h1>API de dados vitivinícolas da Embrapa</h1>
             <p>Selecione uma categoria ao lado para consultar os dados diretamente ou clique abaixo para acessar a documentação Swagger.</p>
             <p><a href="/swagger-ui/">→ Ir para Swagger</a></p>
         </div>
     </body>
     </html>
     '''
     return render_template_string(html, categorias=CSV_URLS.keys())

# Configuração do endpoint para acessar a documentação Swagger UI

if __name__ == '__main__':
    app.run(debug=True)
