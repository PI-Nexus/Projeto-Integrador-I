from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
import time
import html
import re

# cache em memória
df_global = None
info_atualizacao_global = None

def baixar_e_tratar_dados():

    pasta_download = os.path.abspath("downloads")
    global df_global, info_atualizacao_global

    if not os.path.exists(pasta_download):
        os.makedirs(pasta_download)

    caminho_fixo = os.path.join(pasta_download, "cobertura_vacinal.xlsx")

    def precisa_atualizar(caminho):
        tempo_cache = 21600
        if not os.path.exists(caminho):
            return True
        return (time.time() - os.path.getmtime(caminho)) > tempo_cache

    if precisa_atualizar(caminho_fixo):
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

        # Extrai data da última atualização do painel
        kpi_texto = driver.find_element(By.ID, "kpi-container").text
        match = re.search(r'Atualização do painel em (\d{2}/\d{2}/\d{4}) às (\d{2}:\d{2}:\d{2})', kpi_texto)
        if match:
            info_atualizacao = f"{match.group(1)} às {match.group(2)}"
            with open(os.path.join(pasta_download, "ultima_atualizacao.txt"), "w", encoding="utf-8") as f:
                f.write(info_atualizacao)
        else:
            info_atualizacao = None
        info_atualizacao_global = info_atualizacao

        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "aba2-tab"))
        time.sleep(3)
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, "//div[contains(., 'Macrorregiões')]"))
        time.sleep(3)
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "exportar-dados-QV1-10"))
        print("Baixando arquivo...")
        time.sleep(10)
        driver.quit()

        arquivos = [f for f in os.listdir(pasta_download) if f.endswith(".xlsx")]
        arquivos.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_download, x)))
        ultimo = os.path.join(pasta_download, arquivos[-1])

        if ultimo != caminho_fixo:
            if os.path.exists(caminho_fixo):
                os.remove(caminho_fixo)
            os.rename(ultimo, caminho_fixo)

    else:
        # debug
        print("Usando cache (sem Selenium)")
        caminho_kpi = os.path.join(pasta_download, "ultima_atualizacao.txt")
        if os.path.exists(caminho_kpi):
            with open(caminho_kpi, "r", encoding="utf-8") as f:
                info_atualizacao_global = f.read()

    # Lê o Excel e normaliza colunas importantes
    df = pd.read_excel(caminho_fixo)
    if "Município Residência" in df.columns:
        df["Município Residência"] = df["Município Residência"].astype(str).str.strip()
    if "Macrorregião Saúde" in df.columns:
        df["Macrorregião Saúde"] = df["Macrorregião Saúde"].str.strip()
    if "UF Residência" in df.columns:
        df["UF Residência"] = df["UF Residência"].str.strip()
    df_global = df
    return df_global

# nomes dos estados
estados = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba",
    "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia",
    "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}
# Ajusta nomes técnicos das vacinas para algo mais amigável
explicacoes = {
    # "VIP": "(vacina contra poliomielite injetável)",
    "< 30 Dias": "para bebês até 30 dias de vida",
    "<= 1 dia": "aplicada no primeiro dia de vida",
    "<= 2 dias": "aplicada até 2 dias de vida"
}

def buscar_cobertura_estado(estado):
    global df_global

    estado = estado.upper()
    if df_global is None:
        df_global = baixar_e_tratar_dados()

    df = df_global
    colunas_ignorar = [
        " ", "Região Ocorrência", "UF Residência",
        "Macrorregião Saúde", "Região de Saúde",
        "Município Residência", "Imunobiológico"
    ]
    
    # média Brasil (linha onde UF está vazia e região = Brasil)
    df_brasil = df[df[" "] == "Brasil"]

    media_brasil = None

    if not df_brasil.empty:
        linha_brasil = df_brasil.iloc[0]
        valores_brasil = []

        for coluna in df.columns:
            if coluna not in colunas_ignorar:
                valor = linha_brasil[coluna]
                if pd.notna(valor) and valor != "-":
                    valores_brasil.append(float(valor) * 100)

        if valores_brasil:
            media_brasil = round(sum(valores_brasil) / len(valores_brasil), 2)

    try:
        df_filtrado = df[
            (df["UF Residência"] == estado) &
            (df["Macrorregião Saúde"] == "Totais")
        ]

        if df_filtrado.empty:
            return "❌ Estado não encontrado."

        linha = df_filtrado.iloc[0]
        nome_estado = html.escape(estados.get(estado, estado))

        resposta = f"<b>📍 COBERTURA VACINAL — {nome_estado} ({estado})</b>\n"
        resposta += "──────────────────────────\n\n"

        valores = []

        # coleta valores para média
        for coluna in df.columns:
            if coluna not in colunas_ignorar:
                valor = linha[coluna]
                if pd.notna(valor) and valor != "-":
                    valores.append(float(valor) * 100)

        media = round(sum(valores) / len(valores), 2)
        criticos = len([v for v in valores if v < 60])
        alertas = len([v for v in valores if 60 <= v < 75])

        # resumo mais limpo
        resposta += "<b>Indicadores gerais</b>\n"
        resposta += f"Média de cobertura: <b>{media}%</b>\n"

        if criticos > 0:
            resposta += f"🚨 Vacinas críticas: <b>{criticos}</b>\n"
        if alertas > 0:
            resposta += f"⚠️ Em atenção: <b>{alertas}</b>\n"

        resposta += "\n──────────────────────────\n"
        resposta += "<b>Detalhamento por vacina</b>\n"

        # Lista detalhada
        # Percorre todas vacinas e calcula percentuais
        for coluna in df.columns:
            if coluna not in colunas_ignorar:
                valor = linha[coluna]

                if pd.notna(valor) and valor != "-":
                    percentual = round(float(valor) * 100, 2)

                    # status
                    if percentual < 60:
                        status = "— 🚨 Crítico"
                        cor = "🔴"
                    elif percentual < 75:
                        status = "— ⚠️ Atenção"
                        cor = "🟡"
                    else:
                        status = ""
                        cor = "🟢"

                    coluna_tratada = tratar_nome_vacina(coluna)
                    coluna_segura = html.escape(coluna_tratada)

                    # define se precisa quebrar linha (nomes longos)
                    nome_longo = len(coluna_segura) > 35

                    if nome_longo:
                        resposta += f"{cor} {coluna_segura}\n"
                        resposta += f"      <b>{percentual}%</b> {status}\n"
                    else:
                        nome_formatado = coluna_segura.ljust(40, ".")
                        resposta += f"{cor} {nome_formatado} <b>{percentual}%</b> {status}\n"

        # fechamento
        resposta += "\n──────────────────────────\n"
        resposta += "<b>Referência técnica</b>\n"
        resposta += "Cobertura ideal recomendada: <b>acima de 90%</b>\n"

        # comparação com Brasil
        if media_brasil is not None:
            resposta += "\n<b>Comparação nacional</b>\n"
            resposta += f"{nome_estado}: <b>{media}%</b>\n"
            resposta += f"Brasil: <b>{media_brasil}%</b>\n"

            if media < media_brasil:
                resposta += "<b>Classificação:</b> abaixo da média nacional"
            elif media > media_brasil:
                resposta += "<b>Classificação:</b> acima da média nacional"
            else:
                resposta += "<b>Classificação:</b> alinhado à média nacional"
        
        global info_atualizacao_global
        if info_atualizacao_global:
            resposta += "\n──────────────────────────\n"
            resposta += "<b>Ùltima atualização dos dados</b>\n"
            resposta += f"{info_atualizacao_global} \nFonte: Rede Nacional de Dados em Saúde (RNDS)\n"
    
        return resposta

    except Exception as e:
        return f"⚠️ Erro ao processar dados: {e}"

def tratar_nome_vacina(nome):
    nome_tratado = nome
    for chave, explicacao in explicacoes.items():
        if chave in nome:
            nome_tratado = nome.replace(chave, explicacao)
    return nome_tratado

def buscar_municipios_por_estado(estado):
    """
    Retorna lista dos nomes limpos dos municípios disponíveis para um estado.
    Útil para validar entrada do usuário ou listar opções.
    """
    global df_global
    if df_global is None:
        df_global = baixar_e_tratar_dados()

    estado = estado.upper()

    # Linhas de município: UF preenchida, Município preenchido, Macrorregião vazia
    df_mun = df_global[
        (df_global["UF Residência"] == estado) &
        (df_global["Município Residência"].notna()) &
        (df_global["Município Residência"].str.match(r"^\d{6}\s-\s"))
    ]


    municipios = df_mun["Município Residência"].dropna().unique().tolist()
    # Extrai só o nome após o " - "
    return sorted([m.split(" - ", 1)[-1].strip() for m in municipios])


def buscar_cobertura_municipio(estado, municipio):
    global df_global, info_atualizacao_global

    estado = estado.upper()
    municipio_busca = municipio.strip()

    if df_global is None:
        df_global = baixar_e_tratar_dados()

    df = df_global

    colunas_ignorar = [
        " ", "Região Ocorrência", "UF Residência",
        "Macrorregião Saúde", "Região de Saúde",
        "Município Residência", "Imunobiológico"
    ]

    # Filtra por UF e por município — nome pode vir como "530010 - Brasília"
    # então buscamos se o nome digitado aparece após o " - "
    df_mun = df[
        (df["UF Residência"] == estado) &
        (df["Município Residência"].notna()) &
        (df["Município Residência"].str.match(r"^\d{6}\s-\s"))
    ]

    # debug
    print(df_mun["Município Residência"].head(20))
    print(df_mun[df_mun["UF Residência"] == "GO"]["Município Residência"].tolist()[:20])

    import unicodedata

    def normalizar(texto):
        texto = texto.lower().strip()
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
        return texto

    municipio_busca_norm = normalizar(municipio_busca)
    mask = df_mun["Município Residência"].apply(
        lambda x: normalizar(x.split(" - ")[-1]) == municipio_busca_norm
    )

    df_filtrado = df_mun[mask]

    if df_filtrado.empty:
        # Tenta busca parcial para sugerir nomes próximos
        municipios_disponiveis = buscar_municipios_por_estado(estado)
        sugestoes = [m for m in municipios_disponiveis if municipio_busca.lower() in m.lower()]

        msg = f"❌ Município <b>{html.escape(municipio_busca)}</b> não encontrado em {estado}.\n\n"
        if sugestoes:
            msg += "🔍 Você quis dizer?\n"
            for s in sugestoes[:5]:  # máximo 5 sugestões
                msg += f"  • {html.escape(s)}\n"
        else:
            msg += "Verifique o nome e tente novamente."
        return msg

    linha = df_filtrado.iloc[0]
    nome_estado = html.escape(estados.get(estado, estado))
    municipio_seguro = html.escape(municipio_busca)

    resposta = f"<b>📍 COBERTURA VACINAL — {municipio_seguro} / {nome_estado}</b>\n"
    resposta += "──────────────────────────\n\n"

    valores = []
    for coluna in df.columns:
        if coluna not in colunas_ignorar:
            valor = linha[coluna]
            if pd.notna(valor) and valor != "-":
                try:
                    valores.append(float(valor) * 100)
                except (ValueError, TypeError):
                    pass

    if not valores:
        return f"⚠️ Sem dados de cobertura para {municipio_seguro} / {estado}."

    media = round(sum(valores) / len(valores), 2)
    criticos = len([v for v in valores if v < 60])
    alertas = len([v for v in valores if 60 <= v < 75])

    resposta += "<b>Indicadores gerais</b>\n"
    resposta += f"Média de cobertura: <b>{media}%</b>\n"
    if criticos > 0:
        resposta += f"🚨 Vacinas críticas: <b>{criticos}</b>\n"
    if alertas > 0:
        resposta += f"⚠️ Em atenção: <b>{alertas}</b>\n"

    resposta += "\n──────────────────────────\n"
    resposta += "<b>Detalhamento por vacina</b>\n"

    for coluna in df.columns:
        if coluna not in colunas_ignorar:
            valor = linha[coluna]
            if pd.notna(valor) and valor != "-":
                try:
                    percentual = round(float(valor) * 100, 2)
                except (ValueError, TypeError):
                    continue

                if percentual < 60:
                    status, cor = "— 🚨 Crítico", "🔴"
                elif percentual < 75:
                    status, cor = "— ⚠️ Atenção", "🟡"
                else:
                    status, cor = "", "🟢"

                coluna_segura = html.escape(tratar_nome_vacina(coluna))

                if len(coluna_segura) > 35:
                    resposta += f"{cor} {coluna_segura}\n      <b>{percentual}%</b> {status}\n"
                else:
                    resposta += f"{cor} {coluna_segura.ljust(40, '.')} <b>{percentual}%</b> {status}\n"

    resposta += "\n──────────────────────────\n"
    resposta += "Cobertura ideal recomendada: <b>acima de 90%</b>\n"

    if info_atualizacao_global:
        resposta += "\n──────────────────────────\n"
        resposta += f"{info_atualizacao_global}\nFonte: RNDS\n"

    return resposta


def calcular_media_estados():
    global df_global, info_atualizacao_global

    if df_global is None:
        df_global = baixar_e_tratar_dados()

    df = df_global

    colunas_ignorar = [
        " ", "Região Ocorrência", "UF Residência",
        "Macrorregião Saúde", "Região de Saúde",
        "Município Residência", "Imunobiológico"
    ]

    # Linhas de total por estado: UF preenchida + Macrorregião == "Totais"
    # e Região de Saúde vazia (para não pegar subtotais de macrorregião)
    df_totais = df[
        (df["UF Residência"].notna()) &
        (df["UF Residência"] != "") &
        (df["Macrorregião Saúde"] == "Totais") &
        (df["Região de Saúde"].isna() | (df["Região de Saúde"] == ""))
    ]

    resultado = []

    for _, linha in df_totais.iterrows():
        uf = linha.get("UF Residência")
        if not uf or pd.isna(uf):
            continue

        valores = []
        for coluna in df.columns:
            if coluna not in colunas_ignorar:
                valor = linha[coluna]
                if pd.notna(valor) and valor != "-":
                    try:
                        valores.append(float(valor) * 100)
                    except (ValueError, TypeError):
                        pass

        if valores:
            resultado.append((str(uf).strip(), round(sum(valores) / len(valores), 2)))

    resultado.sort(key=lambda x: x[1], reverse=True)

    if not resultado:
        return "⚠️ Não foi possível calcular o ranking."

    resposta = "<b>🇧🇷 COBERTURA VACINAL — RANKING POR ESTADO</b>\n"
    resposta += "──────────────────────────\n\n"

    medalhas = {1: "🥇", 2: "🥈", 3: "🥉"}

    for i, (uf, media) in enumerate(resultado, start=1):
        prefixo = medalhas.get(i, f"{i:>2}.")
        nome = estados.get(uf, uf)
        cor = "🔴" if media < 60 else ("🟡" if media < 75 else "🟢")
        resposta += f"{prefixo} {cor} {uf} — {html.escape(nome)}: <b>{media}%</b>\n"

    media_geral = round(sum(m for _, m in resultado) / len(resultado), 2)
    resposta += "\n──────────────────────────\n"
    resposta += f"<b>Média geral Brasil: {media_geral}%</b>\n"

    if info_atualizacao_global:
        resposta += "\n──────────────────────────\n"
        resposta += f"{info_atualizacao_global}\nFonte: RNDS\n"

    return resposta