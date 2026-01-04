import os
import logging
from flask import Flask
from flask_restx import Api, Resource, reqparse
import pandas as pd

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="API de Projeção ITUB4 - Pós Tech Fase 4",
    description="API para consulta de projeções (Pessimista, Mediana, Otimista) a partir de CSV.",
    doc="/",
)

ns = api.namespace("finance", description="Operações com projeções financeiras")

# procura CSV no mesmo diretório do script
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
CANDIDATES = [
    "outputs/projecao_itub4_cenarios_ate_2026.csv",
    "dados_yfinance.csv",
]
CSV_PATH = None
for name in CANDIDATES:
    p = os.path.join(BASE_DIR, name)
    if os.path.exists(p):
        CSV_PATH = p
        break
if CSV_PATH is None:
    for f in os.listdir(BASE_DIR):
        if f.lower().endswith(".csv"):
            CSV_PATH = os.path.join(BASE_DIR, f)
            break
if CSV_PATH is None:
    raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {BASE_DIR}. Procure por: {CANDIDATES}")

logging.info(f"Lendo CSV: {CSV_PATH}")

df_raw = pd.read_csv(CSV_PATH)
df_raw.columns = df_raw.columns.str.strip()

# valida exatamente as colunas esperadas
expected = {"Date", "Pessimista", "Mediana", "Otimista"}
missing = expected - set(df_raw.columns)
if missing:
    raise RuntimeError(
        f"CSV inválido. Faltando colunas: {sorted(missing)}. Colunas presentes: {df_raw.columns.tolist()}"
    )

# parse da data
df_raw["Date"] = pd.to_datetime(df_raw["Date"], errors="coerce", dayfirst=True)

# converte cenários para numérico (caso venham como string)
for col in ["Pessimista", "Mediana", "Otimista"]:
    df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

# transforma para formato "longo": (Date, Cenario, Valor)
df = df_raw.melt(
    id_vars=["Date"],
    value_vars=["Pessimista", "Mediana", "Otimista"],
    var_name="cenario",
    value_name="valor",
).sort_values(["cenario", "Date"])

# Como o arquivo é específico do ITUB4, definimos um ticker fixo
DEFAULT_TICKER = "ITUB4.SA"
df["Ticker"] = DEFAULT_TICKER

# Parsers
ticker_parser = reqparse.RequestParser()
ticker_parser.add_argument("ticker", type=str, required=False, help="Ticker (padrão: ITUB4.SA)")

cenario_parser = reqparse.RequestParser()
cenario_parser.add_argument("ticker", type=str, required=False, help="Ticker (padrão: ITUB4.SA)")
cenario_parser.add_argument("cenario", type=str, required=False, choices=["Pessimista", "Mediana", "Otimista"],
                            help="Cenário: Pessimista | Mediana | Otimista")

@ns.route("/stocks")
class ListaTickers(Resource):
    """Lista tickers disponíveis (neste dataset, apenas ITUB4.SA)."""
    def get(self):
        return {"tickers_disponiveis": [DEFAULT_TICKER]}

@ns.route("/scenarios")
class ListaCenarios(Resource):
    """Lista os cenários disponíveis no CSV."""
    def get(self):
        return {"cenarios_disponiveis": ["Pessimista", "Mediana", "Otimista"]}

@ns.route("/projection")
class Projecao(Resource):
    """
    Retorna as projeções por data.
    - Se passar cenario, retorna apenas aquele cenário.
    - Se não passar, retorna todos os cenários.
    """
    @ns.expect(cenario_parser)
    def get(self):
        args = cenario_parser.parse_args()
        ticker = (args.get("ticker") or DEFAULT_TICKER).strip().upper()
        cenario = args.get("cenario")

        # dataset é somente ITUB4.SA
        if ticker != DEFAULT_TICKER:
            api.abort(404, f"Ticker '{ticker}' não encontrado. Dataset contém apenas '{DEFAULT_TICKER}'.")

        # work on a copy so we don't mutate the global dataframe
        data = df.copy()
        if cenario:
            data = data[data["cenario"] == cenario].copy()

        # convert pandas Timestamps to ISO strings for JSON serialization
        if "Date" in data.columns:
            data["Date"] = data["Date"].apply(lambda x: x.isoformat() if pd.notnull(x) else None)

        registros = data.where(pd.notnull(data), None).to_dict(orient="records")
        return {"ticker": ticker, "cenario": cenario, "dados": registros}

@ns.route("/summary")
class Resumo(Resource):
    """Resumo estatístico das projeções (por cenário opcional)."""
    @ns.expect(cenario_parser)
    def get(self):
        args = cenario_parser.parse_args()
        ticker = (args.get("ticker") or DEFAULT_TICKER).strip().upper()
        cenario = args.get("cenario")

        if ticker != DEFAULT_TICKER:
            api.abort(404, f"Ticker '{ticker}' não encontrado. Dataset contém apenas '{DEFAULT_TICKER}'.")

        data = df
        if cenario:
            data = data[data["cenario"] == cenario]

        if data["valor"].dropna().empty:
            api.abort(404, "Não há valores numéricos válidos para calcular o resumo.")

        resumo = {
            "ticker": ticker,
            "cenario": cenario or "TODOS",
            "media": round(data["valor"].mean(), 2),
            "maximo": round(data["valor"].max(), 2),
            "minimo": round(data["valor"].min(), 2),
            "primeira_data": None,
            "ultima_data": None,
        }

        # datas (se válidas)
        valid_dates = data["Date"].dropna()
        if not valid_dates.empty:
            resumo["primeira_data"] = valid_dates.min().date().isoformat()
            resumo["ultima_data"] = valid_dates.max().date().isoformat()

        return resumo

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
