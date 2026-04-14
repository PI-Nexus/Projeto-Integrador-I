from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time

def baixar_e_tratar_dados():

    pasta_download = os.path.abspath("downloads")

    if not os.path.exists(pasta_download):
        os.makedirs(pasta_download)

    caminho_fixo = os.path.join(pasta_download, "cobertura_vacinal.xlsx")

    def precisa_atualizar(caminho):
        tempo_cache = 21600  # 6 horas

        if not os.path.exists(caminho):
            return True

        tempo_modificacao = os.path.getmtime(caminho)
        agora = time.time()

        return (agora - tempo_modificacao) > tempo_cache

    # Só roda Selenium se precisar
    if precisa_atualizar(caminho_fixo):

        # Deploy
        print("Atualizando base de dados...")

        options = Options()
        prefs = {
            "download.default_directory": pasta_download,
            "download.prompt_for_download": False
        }
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)

        driver.get("https://infoms.saude.gov.br/extensions/SEIDIGI_DEMAS_VACINACAO_CALENDARIO_NACIONAL_COBERTURA_RESIDENCIA/SEIDIGI_DEMAS_VACINACAO_CALENDARIO_NACIONAL_COBERTURA_RESIDENCIA.html")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)

        aba = wait.until(EC.presence_of_element_located((By.ID, "aba2-tab")))
        driver.execute_script("arguments[0].click();", aba)
        time.sleep(3)

        macro = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(., 'Macrorregiões')]")))
        driver.execute_script("arguments[0].click();", macro)
        time.sleep(3)

        download = wait.until(EC.presence_of_element_located((By.ID, "exportar-dados-QV1-10")))
        driver.execute_script("arguments[0].click();", download)

        print("Baixando novo arquivo...")
        time.sleep(10)

        driver.quit()

        # pega o último arquivo baixado
        arquivos = [f for f in os.listdir(pasta_download) if f.endswith(".xlsx")]
        arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_download, x)))

        ultimo = os.path.join(pasta_download, arquivos[-1])

        # substitui o antigo
        if os.path.exists(caminho_fixo):
            os.remove(caminho_fixo)

        os.rename(ultimo, caminho_fixo)

    else:
        # Deploy
        print("Usando cache (sem abrir Selenium)")

    # lê o arquivo final
    df = pd.read_excel(caminho_fixo)

    return df

# lista de estados para exibir nome completo
estados = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins"
}

def buscar_cobertura_estado(estado):
    import pandas as pd

    df = baixar_e_tratar_dados()
    estado = estado.upper()

    try:
        # Filtra apenas dados no nível de estado (linha "Totais")
        df_filtrado = df[
            (df["UF Residência"] == estado) &
            (df["Macrorregião Saúde"] == "Totais")
        ]

        if df_filtrado.empty:
            return "❌ Estado não encontrado."

        linha = df_filtrado.iloc[0]
        
        nome_estado = estados.get(estado, estado)
        resposta = f"📍 *Cobertura Vacinal em {nome_estado} ({estado})*\n\n"
        
        # Remove colunas que não representam vacinas
        colunas_ignorar = [
            " ", "Região Ocorrência", "UF Residência",
            "Macrorregião Saúde", "Região de Saúde",
            "Município Residência", "Imunobiológico"
        ]

        for coluna in df.columns:
            if coluna not in colunas_ignorar:
                valor = linha[coluna]

                if pd.notna(valor) and valor != "-":
                    percentual = round(float(valor) * 100, 2)

                    # define alerta
                    alerta = ""
                    if percentual < 60:
                        alerta = "      🚨 baixa cobertura"
                    elif percentual < 75:
                        alerta = "      ⚠️ atenção"
                    else:
                        alerta = ""

                    # formata resposta
                    resposta += f" •  {coluna} {percentual}% {alerta}\n"

        return resposta

    except Exception as e:
        return f"⚠️ Erro ao processar dados: {e}"