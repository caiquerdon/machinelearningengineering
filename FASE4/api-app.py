from flask import Flask
from flask_restx import Api, Resource, reqparse
import pandas as pd

#
app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="API de Dados Financeiros - Pós Tech Fase 4",
    description="API construída em Flask para consulta de dados coletados via YFinance.",
    doc="/", 
)


ns = api.namespace("finance", description="Operações com dados financeiros")


CSV_PATH = "dados_yfinance.csv"


df = pd.read_csv(CSV_PATH)
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")


parser = reqparse.RequestParser()
parser.add_argument("ticker", type=str, required=True, help="Código do ativo (ex: PETR4.SA)")

@ns.route("/stocks")
class ListaTickers(Resource):
    """Lista todos os tickers disponíveis."""
    def get(self):
        tickers = sorted(df["Ticker"].unique().tolist())
        return {"tickers_disponiveis": tickers}

@ns.route("/stock")
class DadosTicker(Resource):
    """Retorna os dados completos de um ticker específico."""
    @ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        ticker = args["ticker"]
        dados_ticker = df[df["Ticker"].str.upper() == ticker.upper()]
        if dados_ticker.empty:
            api.abort(404, f"Nenhum dado encontrado para o ticker '{ticker}'")
        registros = dados_ticker.to_dict(orient="records")
        return {"ticker": ticker.upper(), "dados": registros}

@ns.route("/summary")
class ResumoTicker(Resource):
    """Retorna um resumo estatístico do ticker."""
    @ns.expect(parser)
    def get(self):
        args = parser.parse_args()
        ticker = args["ticker"]
        dados_ticker = df[df["Ticker"].str.upper() == ticker.upper()]
        if dados_ticker.empty:
            api.abort(404, f"Nenhum dado encontrado para o ticker '{ticker}'")

        resumo = {
            "ticker": ticker.upper(),
            "media_fechamento": round(dados_ticker["Fechamento"].mean(), 2),
            "maxima": round(dados_ticker["Alta"].max(), 2),
            "minima": round(dados_ticker["Baixa"].min(), 2),
            "volume_medio": int(dados_ticker["Volume"].mean()),
        }
        return resumo

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

