import re
from datetime import datetime

def extrair_ano(texto):

    anos = re.findall(r"\b(19\d{2}|20\d{2})\b", texto)

    if anos:
        return int(anos[0])

    return None


def extrair_data(texto):

    padrao = r"(\d{1,2}/\d{1,2}/\d{4})"

    match = re.search(padrao, texto)

    if match:
        return match.group(1)

    return None


def extrair_idade(texto):

    texto = texto.lower()

    match = re.search(r"(\d+)\s*anos?", texto)

    if match:
        return int(match.group(1))

    return None


def idade_para_data(idade):

    ano_atual = datetime.now().year

    ano_nascimento = ano_atual - idade

    return f"01/01/{ano_nascimento}"

def extrair_idade_meses(texto):
    """Retorna idade em meses se mencionado, senão None"""
    texto = texto.lower()
    match = re.search(r'(\d+)\s*m[eê]s(?:es)?', texto)
    if match:
        return int(match.group(1))
    return None

def meses_para_data(meses):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    return (datetime.now() - relativedelta(months=meses)).strftime("%d/%m/%Y")

# PARTE DE COBERTURA

from src.scrap_cobertura import estados

import re
import unicodedata
from src.scrap_cobertura import estados

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

def extrair_estado(texto):
    texto_norm = normalizar(texto)

    # 1. Busca por nome completo primeiro (mais confiável)
    for uf, nome in estados.items():
        nome_norm = normalizar(nome)
        # word boundary no nome
        if re.search(rf"\b{re.escape(nome_norm)}\b", texto_norm):
            return uf

    # 2. Busca por sigla — só word boundary, evita "ac" em "vacinal"
    for uf in estados:
        if re.search(rf"\b{re.escape(uf.lower())}\b", texto_norm):
            return uf

    return None