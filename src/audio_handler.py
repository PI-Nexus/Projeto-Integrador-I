import os
import re
import tempfile
import requests
from faster_whisper import WhisperModel

whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

# lista de palavras que o bot vai reconhecer nos áudios, agrupadas por categoria 
PALAVRAS_CHAVE = [
    (
        "unidades_proximas",
        [
            "ubs", "posto", "postinho", "unidade", "proximo", "perto", "localizacao", "lugar",
            "onde", "aonde", "proximas",
        ],
    ),
    (
        "cobertura_vacinal",
        [
            "cobertura", "indice", "porcentagem", "percentual", "estado", "municipio", "cidade",
            "regiao", "ranking", "dashboard",
        ],
    ),
    (
        "vacinas",
        [
            "vacina", "vacinas", "tomar vacina", "se vacinar", "dose", "imunizacao", "imunizar",
            "agendar",
        ],
    ),
    (
        "faq",
        [
            "duvida", "pergunta", "documento", "perguntas", "reacao", "duvidas", "faq", "informacao",
        ],
    ),
    (
        "encerrar",
        [
            "encerrar", "sair", "fechar", "finalizar", "terminar", "desligar", "parar", "obrigado",
            "obrigada", "tchau", "ate mais", "ate logo", "ate breve", "ate a proxima",
        ],
    ),
    (
        "inicio",
        [
            "inicio", "menu", "comeco", "voltar", "ajuda", "oi",
            "ola", "bom dia", "boa tarde", "boa noite",
        ],
    ),
]

# função para normalizar o texto removendo acentos e cecidilha
def normalizar(texto: str) -> str:
    mapa = str.maketrans(
        "àáâãäçèéêëìíîïòóôõöùúûüýÀÁÂÃÄÇÈÉÊËÌÍÎÏÒÓÔÕÖÙÚÛÜÝ",
        "aaaааceeeeiiiiooooouuuuyAAAAACEEEEIIIIOOOOOUUUUY",
    )
    return texto.lower().translate(mapa)

# função que baixa o áudio e o salva em um arquivo temporário
def baixar_audio(bot, file_id: str) -> str:
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
    extensao = os.path.splitext(file_info.file_path)[-1] or ".ogg"

    response = requests.get(file_url)
    response.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=extensao)
    tmp.write(response.content)
    tmp.close()
    return tmp.name

# função que faz a transcrição do áudio
def transcrever_audio(caminho_arquivo: str) -> str:
    segments, _ = whisper_model.transcribe(
        caminho_arquivo,
        language="pt",
        beam_size=5,
    )
    return " ".join(seg.text.strip() for seg in segments).strip()

# função que classifica o áudio com base nas palavras chaves definidas
def classificar_comando(texto: str) -> dict:
    texto_normalizado = normalizar(texto)
    for categoria, palavras in PALAVRAS_CHAVE:
        for palavra in palavras:
            palavra_normalizada = normalizar(palavra)
            if re.search(rf"\b{re.escape(palavra_normalizada)}\b", texto_normalizado):
                return {
                    "categoria": categoria, 
                    "palavra_chave": palavra
                }
    return {
        "categoria": "desconhecido", 
        "palavra_chave": None
    }

# execução do pipeline completo de baixar, transcrever e classificar o áudio, 
# e também removendo o arquivo temporário após o processo
def processar_audio(bot, file_id: str) -> dict:
    caminho_arquivo = None
    try:
        caminho_arquivo = baixar_audio(bot, file_id)
        transcricao = transcrever_audio(caminho_arquivo)
        transcricao_adaptada = normalizar(transcricao)
        classificacao = classificar_comando(transcricao_adaptada)
        return {"transcricao": transcricao_adaptada, **classificacao}
    finally:
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)