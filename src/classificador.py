import re
import ollama

FAQ_KEYWORDS = [
    "o que é", "o que sao", "o que são", "como funciona", "para que serve",
    "imunidade", "imunização", "efeito colateral", "reação", "dói", "doi",
    "posso", "preciso", "devo", "tenho que", "depois de vacinar", "antes de vacinar",
    "documento", "caderneta", "sus", "campanha"
]

VACINA_IDADE_REGEX = [
    r'\d{1,2}/\d{1,2}/\d{4}',           # data DD/MM/AAAA
    r'\b(19|20)\d{2}\b',                  # ano de nascimento
    r'\b\d+\s*anos?\b',                   # N anos
    r'\b\d+\s*m[eê]s(es)?\b',            # N meses
    r'\bnasci\b',                         # nasci
    r'\bidade\b',                         # idade
]

def classificar_intencao(texto_usuario):
    texto_lower = texto_usuario.lower()

    # 1. VACINA_IDADE por regex — tem prioridade máxima
    for padrao in VACINA_IDADE_REGEX:
        if re.search(padrao, texto_lower):
            return "VACINA_IDADE"

    # 2. VACINA_GRUPO por keyword
    grupos = ["criança", "crianca", "adolescente", "adulto", "idoso", "gestante"]
    for g in grupos:
        if g in texto_lower:
            return "VACINA_GRUPO"

    # 3. FAQ por keyword
    for kw in FAQ_KEYWORDS:
        if kw in texto_lower:
            return "FAQ"

    # 4. UBS/localização por keyword
    if any(p in texto_lower for p in ["ubs", "posto de saúde", "unidade", "próximas"]):
        return "LOCALIZACAO"

    # 5. Classificador LLM para o resto
    prompt = f"""Você é um classificador de intenções de um bot de vacinação brasileiro.

Classifique a mensagem e retorne SOMENTE UMA opção sem explicação:

VACINA_IDADE - menciona idade, data, ano de nascimento
VACINA_GRUPO - menciona criança, adolescente, adulto, idoso, gestante
FAQ - dúvidas e perguntas sobre vacinas, saúde, reações, imunidade
COBERTURA_ESTADO - cobertura de um estado ou sigla. Ex: "Cobertura SP"
COBERTURA_MUNICIPIO - cobertura quando menciona cidade. Ex: "Cobertura Campinas SP", "cobertura Maragogi"
RANKING_ESTADOS - ranking, comparação entre estados
LOCALIZACAO - posto de saúde, UBS, unidade próxima
FORA_DO_ESCOPO - qualquer outro assunto

Mensagem: {texto_usuario}

Responda com apenas uma palavra."""

    resposta = ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": prompt}]
    )

    resultado = resposta["message"]["content"].strip().upper()
    primeira_palavra = re.sub(r'[^A-Z_]', '', resultado.split()[0]) if resultado.split() else ""

    validas = {
        "FAQ", "VACINA_IDADE", "VACINA_GRUPO",
        "COBERTURA_ESTADO", "COBERTURA_MUNICIPIO",
        "RANKING_ESTADOS", "LOCALIZACAO", "FORA_DO_ESCOPO"
    }

    return primeira_palavra if primeira_palavra in validas else "FORA_DO_ESCOPO"