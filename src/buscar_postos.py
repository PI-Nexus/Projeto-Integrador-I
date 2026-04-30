# Bibliotecas padrão (Python)
import os
import math
import threading
from threading import Lock


# Bibliotecas externas
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options


options = Options()
options.add_argument("--headless=new") # roda Chrome sem interface gráfica
options.add_argument("--disable-dev-shm-usage") # Evita problemas com memória compartilhada r
options.add_argument("--no-sandbox") # Desativa o sandbox de segurança do Chrome

lock=Lock()
# CARREGAR CSV

arquivo = "Unidade_basica_de_saude.csv"

base_dir = os.path.dirname(__file__)
caminho = os.path.join(base_dir, arquivo)


df = pd.read_csv(caminho, sep=";")

# Corrigir espaços nos nomes das colunas
df.columns = df.columns.str.strip()

# TRATAMENTO DE DADOS

# Corrigir longitude (trocar vírgula por ponto)
df["LONGITUDE"] = df["LONGITUDE"].astype(str).str.replace(",", ".")

# Função para corrigir latitude quebrada
def corrigir_lat(valor):
    try:
        valor = str(valor).replace(".", "")

        # Garante que começa com sinal negativo
        if not valor.startswith("-"):
            return None

        # Remove o sinal para manipular
        numero = valor[1:]

        # Reconstrói: -XX.xxxxxx
        if len(numero) >= 4:
            corrigido = "-" + numero[:2] + "." + numero[2:]
            return float(corrigido)

        return None
    except:
        return None

df["LATITUDE"] = df["LATITUDE"].apply(corrigir_lat)

# Converter para número
df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")

# Remover dados inválidos
df = df.dropna(subset=["LATITUDE", "LONGITUDE"])


#  DISTÂNCIA

#  Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine.
def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

#  BUSCA

#Busca os postos mais próximos de um usuário com base na latitude e longitude.
def buscar_postos_proximos(user_lat, user_lon):
    df_local = df[
        (df["LATITUDE"].between(user_lat - 0.5, user_lat + 0.5)) &
        (df["LONGITUDE"].between(user_lon - 0.5, user_lon + 0.5))]
    resultados = []

    for _, row in df_local.iterrows():

        distancia = haversine(user_lat, user_lon, row["LATITUDE"], row["LONGITUDE"])

        resultados.append({
            "nome": row["NOME"],
            "endereco": f"{row['LOGRADOURO']}, {row['BAIRRO']}",
            "distancia": round(distancia, 2),
            "lat":row["LATITUDE"],
            "lon":row["LONGITUDE"]
        })

    resultados.sort(key=lambda x: x["distancia"])
    return resultados[:4]
# ------------------ TESTE ------------------

def retorno_link_maps(data,driver,links):
    try:
        lat_ubs, lon_ubs = data['lat'], data['lon']
        name=str(data['nome']).title().replace(" ", "+")
        maps = f"https://www.google.com/maps/@{lat_ubs},{lon_ubs},14z"
        # Abre o site
        driver.get(maps)

        # Encontra a barra de pesquisa, digita e busca
        search_bar = driver.find_element(By.NAME, "q")
        search_bar.send_keys(name)
        search_bar.send_keys(Keys.RETURN)

        url = driver.current_url

        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != url
        )
        # Adiciona link a uma variavel global (links)
        with lock:
            links[data['nome']]= driver.current_url
    except:
        return None

# inicializa drivers e impede ativação paralela da função start_drivers()
drivers = []
initializing = False
def start_drivers():
    global drivers, initializing

    if drivers or initializing:
        return

    initializing = True
    drivers = [
        webdriver.Chrome(options=options),
        webdriver.Chrome(options=options),
        webdriver.Chrome(options=options),
        webdriver.Chrome(options=options)
    ]
    initializing = False

def threading_search(postos):
    links={}
    t1,t2,t3,t4=(
    threading.Thread(target=retorno_link_maps,args=(postos[0],drivers[0],links)),
    threading.Thread(target=retorno_link_maps,args=(postos[1],drivers[1],links)),
    threading.Thread(target=retorno_link_maps,args=(postos[2],drivers[2],links)),
    threading.Thread(target=retorno_link_maps,args=(postos[3],drivers[3],links)))

    t1.start(),t2.start(),t3.start(),t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    for driver in drivers:
        driver.quit()
    drivers.clear()
    return links
