import pdfplumber
import requests
import json
import os
import re

# =============================================================================
# CONFIGURAÇÕES E TRADUÇÕES
# =============================================================================
TRADUCAO_NUMEROS = {
    "um": "1", "uma": "1", "dois": "2", "duas": "2",
    "tres": "3", "três": "3", "quatro": "4", "cinco": "5", "seis": "6"
}

# Caminhos organizados
BASE_PATH = "pasta-venv"
ARQUIVOS_LOCAIS = {
    "adolescente": os.path.join(BASE_PATH, "adolescente-Calend.pdf"),
    "adulto":      os.path.join(BASE_PATH, "adulto-Calend.pdf"),
    "idoso":       os.path.join(BASE_PATH, "idoso-Calend.pdf"),
    "prematuro":   os.path.join(BASE_PATH, "prematuro-Calend.pdf"),
    "crianca":     os.path.join(BASE_PATH, "crianca-Calend.pdf"),
}

ARQUIVOS_REMOTOS = {} # Caso precise baixar algo futuramente
ARQUIVO_SAIDA = "calendario_completo.json"

# =============================================================================
# 1. UTILITÁRIOS DE PARSING
# =============================================================================

def limpar(texto):
    return " ".join(texto.split()).strip() if texto else ""

def normalizar_texto_para_regex(texto):
    texto_limpo = texto.lower()
    for palavra, numero in TRADUCAO_NUMEROS.items():
        texto_limpo = re.sub(rf'\b{palavra}\b', numero, texto_limpo)
    return texto_limpo

def parsear_esquema(texto_periodo):
    if not texto_periodo: 
        return _esquema_vazio()
    
    texto = normalizar_texto_para_regex(texto_periodo)
    esquema = _esquema_vazio()

    # Dose única
    if re.search(r'\bdose\s+[úu]nica\b', texto):
        esquema.update({"dose_unica": True, "total_doses": 1})
        return esquema

    # Total de doses
    match_doses = re.search(r'(\d+)\s+doses?', texto)
    if match_doses: 
        esquema["total_doses"] = int(match_doses.group(1))

    # Intervalos (Ex: 0-2-4-6 meses)
    unidades = {"dia": 1, "semana": 7, "mês": 30, "mes": 30, "ano": 365}
    match_seq = re.search(r'((?:\d+\s*[-–/]\s*)+\d+)\s*(dias?|semanas?|m[eê]s|meses|anos?)', texto)
    
    if match_seq:
        pontos = [int(p.strip()) for p in re.split(r'[-–/]', match_seq.group(1)) if p.strip().isdigit()]
        unidade_raw = match_seq.group(2).lower().rstrip('es').rstrip('s')
        fator = unidades.get(unidade_raw, 30)

        if len(pontos) >= 2:
            if not esquema["total_doses"]: esquema["total_doses"] = len(pontos)
            for i in range(len(pontos) - 1):
                diff = pontos[i+1] - pontos[i]
                esquema["intervalo_entre_doses"].append({
                    "de_dose": i+1, "para_dose": i+2,
                    "intervalo_dias": diff * fator,
                    "intervalo_texto": f"{diff} {match_seq.group(2)}"
                })
    
    reforco_match = re.findall(r'refor[çc]o[^.;]*(?:\.|\;|$)', texto)
    esquema["reforcos"] = [r.strip().capitalize() for r in reforco_match]
    return esquema

def _esquema_vazio():
    return {"total_doses": None, "dose_unica": False, "intervalo_entre_doses": [], "reforcos": []}

# =============================================================================
# 2. EXTRAÇÃO E PROCESSAMENTO
# =============================================================================

def extrair_dados(caminho, categoria):
    dados = []
    # Palavras-chave para ignorar linhas de cabeçalho
    ignorar = {"vacina", "doença", "esquema", "recomendações", "idade"}
    
    try:
        with pdfplumber.open(caminho) as pdf:
            for page in pdf.pages:
                tabela = page.extract_table()
                if not tabela: continue
                
                for linha in tabela:
                    # Limpa células e remove itens nulos
                    linha_limpa = [limpar(c) for c in linha if c is not None]
                    
                    if len(linha_limpa) < 2: continue
                    
                    nome_vacina = linha_limpa[0]
                    if not nome_vacina or nome_vacina.lower() in ignorar:
                        continue

                    # Lógica inteligente de colunas:
                    # Geralmente: [0] Vacina, [1] Doença, [2] Esquema
                    # Vamos tentar pegar a coluna que parece ter números ou prazos
                    esquema_raw = ""
                    for cell in linha_limpa[1:]:
                        if any(char.isdigit() for char in cell) or "dose" in cell.lower():
                            esquema_raw = cell
                            break
                    
                    if not esquema_raw: esquema_raw = linha_limpa[1]

                    dados.append({
                        "vacina": nome_vacina,
                        "categoria": categoria,
                        "texto_original": esquema_raw,
                        "esquema_parseado": parsear_esquema(esquema_raw)
                    })
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
        
    return dados

def processar():
    resultado_final = []
    
    # Processa cada arquivo local definido
    for categoria, caminho in ARQUIVOS_LOCAIS.items():
        if os.path.exists(caminho):
            print(f"Lendo: {caminho} ({categoria})")
            dados_extraidos = extrair_dados(caminho, categoria)
            resultado_final.extend(dados_extraidos)
        else:
            print(f"Arquivo não encontrado: {caminho}")

    # Salva o resultado
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=4)
    
    print(f"\nSucesso! {len(resultado_final)} registros salvos em '{ARQUIVO_SAIDA}'.")

if __name__ == "__main__":
    processar()