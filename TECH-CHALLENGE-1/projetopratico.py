# Montar uma API com o Flask para consumir os dados da EMBRAPA

# DEFINIR ARQUITETURA - OK
# CRIAR CONTA AWS

from flask import Flask, jsonify
import pandas as pd
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

URL = "http://vitibrasil.cnpuv.embrapa.br/download/Producao.csv"
PASTA_SAIDA = "TECH-CHALLENGE-1/download"
ARQUIVO_JSON = "producao_uvas_2023.json"

def extrair_tabela(url):
    """
    Extrai a primeira tabela da página usando Selenium.
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(2)  # Aguarda carregamento da página

        # Extrai o HTML da tabela
        tabelas_html = driver.find_elements(By.TAG_NAME, "table")
        if not tabelas_html:
            driver.quit()
            return "Nenhuma tabela encontrada na página."

        tabela_html = tabelas_html[0].get_attribute('outerHTML')
        driver.quit()

        tabela_dados = pd.read_html(tabela_html, decimal=",", thousands=".")[0]
        tabela_dados.columns = [col.strip() for col in tabela_dados.columns]
        return tabela_dados
    except Exception as e:
        return str(e)

def salvar_json_local(df, pasta, nome_arquivo):
    caminho_pasta = os.path.join(os.getcwd(), pasta)
    os.makedirs(caminho_pasta, exist_ok=True)
    caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
    return caminho_arquivo

@app.route('/dados', methods=['GET'])
def get_dados():
    tabela = extrair_tabela(URL)
    if isinstance(tabela, str):
        return jsonify({"erro": tabela}), 500

    caminho = salvar_json_local(tabela, PASTA_SAIDA, ARQUIVO_JSON)
    return jsonify({
        "mensagem": "Dados extraídos e salvos com sucesso.",
        "caminho_arquivo": caminho
    })

if __name__ == '__main__':
    app.run(debug=True)
