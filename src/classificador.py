import ollama

def classificar_intencao(texto_usuario):

    prompt = f"""Você é um classificador de intenções de um bot de vacinação brasileiro.

Classifique a mensagem e retorne SOMENTE UMA opção sem explicação:

VACINA_IDADE - quando menciona idade, data de nascimento, ano. Ex: "tenho 18 anos", "nasci em 2000", "vacinas para 5 anos", "meu filho tem 3 meses"
FAQ - dúvidas, perguntas sobre vacinas, saúde, reações, dor, descanso, cuidados, imunidade, efeitos colaterais. Ex: "preciso repousar?", "dói tomar vacina?", "posso beber depois?"
VACINA_GRUPO - SOMENTE quando menciona explicitamente: criança, adolescente, adulto, idoso, gestante. Nunca classifique idade numérica aqui.
COBERTURA_ESTADO - cobertura de um estado ou sigla isolada. Ex: "Cobertura SP", "Cobertura Minas Gerais"
COBERTURA_MUNICIPIO - cobertura quando menciona nome de cidade. Ex: "Cobertura Campinas SP", "Cobertura de São Paulo capital", "cobertura vacinal de Aparecida SP"
RANKING_ESTADOS - ranking, comparação entre estados
LOCALIZACAO - posto de saúde, UBS, unidade próxima
FORA_DO_ESCOPO - qualquer outro assunto não relacionado a vacinação

Mensagem: {texto_usuario}

Responda com apenas uma palavra."""

    resposta = ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": prompt}]
    )

    resultado = resposta["message"]["content"].strip().upper()

    # Pega só a primeira palavra (caso o modelo devolva algo extra)
    primeira_palavra = resultado.split()[0] if resultado.split() else ""

    validas = {
        "MENU", "FAQ", "VACINA_IDADE", "VACINA_GRUPO",
        "COBERTURA_ESTADO", "COBERTURA_MUNICIPIO",
        "RANKING_ESTADOS", "LOCALIZACAO", "FORA_DO_ESCOPO"
    }

    return primeira_palavra if primeira_palavra in validas else "FORA_DO_ESCOPO"