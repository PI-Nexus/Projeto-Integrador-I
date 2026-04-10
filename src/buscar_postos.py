import pandas as pd
import math
import os

# ------------------ CARREGAR CSV ------------------

base_dir = os.path.dirname(__file__)
caminho = os.path.join(base_dir, "Unidade_basica_de_saude.csv")

df = pd.read_csv(caminho, sep=";")

# Corrigir espaços nos nomes das colunas
df.columns = df.columns.str.strip()

# ------------------ LIMPEZA ------------------

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

# Remover inválidos
df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

# ------------------ DISTÂNCIA ------------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

# ------------------ BUSCA ------------------

def buscar_postos_proximos(user_lat, user_lon):
    resultados = []

    for _, row in df.iterrows():
        distancia = haversine(user_lat, user_lon, row["LATITUDE"], row["LONGITUDE"])

        resultados.append({
            "nome": row["NOME"],
            "endereco": f"{row['LOGRADOURO']}, {row['BAIRRO']}",
            "distancia": round(distancia, 2)
        })

    resultados.sort(key=lambda x: x["distancia"])
    return resultados[:5]

# ------------------ TESTE ------------------

if __name__ == "__main__":
    # Teste local: exibe os 5 postos mais próximos para uma coordenada exemplo
    print(buscar_postos_proximos(-8.68, -35.58))