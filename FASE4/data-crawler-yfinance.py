import yfinance as yf
import pandas as pd
from datetime import datetime


TICKERS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
START_DATE = "2023-01-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")


OUTPUT_FILE = "dados_yfinance.csv"

def baixar_dados_yfinance(tickers, start, end):
    df = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True)
    return df

def transformar_dados(df):
    df_flat = df.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index()
    df_flat.columns = ["Data", "Ticker", "Abertura", "Alta", "Baixa", "Fechamento", "Volume"]
    return df_flat

def salvar_csv(df, output_file):
    df.to_csv(output_file, index=False)
    print("Arquivo salvo com sucesso!")

def main():
    df_raw = baixar_dados_yfinance(TICKERS, START_DATE, END_DATE)
    df_final = transformar_dados(df_raw)
    salvar_csv(df_final, OUTPUT_FILE)
    print(df_final.head())

if __name__ == "__main__":
    main()
