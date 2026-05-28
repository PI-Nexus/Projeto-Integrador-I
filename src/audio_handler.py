import os
import logging
import tempfile
import requests
import ollama
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

OLLAMA_MODEL = "llama3.2:latest"

SYSTEM_PROMPT = """\
Você é o Assistente Gotinha, especializado em vacinação e saúde pública.

Analise a mensagem do usuário e responda com UMA das opções abaixo:

Se o usuário quer iniciar, cumprimentar ou pedir ajuda:
FUNCAO: inicio

Se o usuário quer saber sobre cobertura vacinal, índices ou ranking por região:
FUNCAO: cobertura_vacinal

Se o usuário quer encontrar UBS, posto de saúde ou unidade próxima:
FUNCAO: localizacao

Se o usuário quer saber quais vacinas tomar, consultar calendário vacinal ou situação vacinal:
FUNCAO: consulta_vacinas

Se o usuário quer encerrar, se despedir ou agradecer:
FUNCAO: fim

Se o usuário fez uma pergunta sobre vacinas, doenças, efeitos colaterais ou saúde:
RESPOSTA: <responda de forma clara, humana e objetiva, sem inventar informações médicas>

Responda APENAS com uma das linhas acima. Nada mais.
"""


def baixar_audio(bot, file_id: str) -> str:
    """Baixa o áudio do Telegram e salva em arquivo temporário."""
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
    extensao = os.path.splitext(file_info.file_path)[-1] or ".ogg"

    response = requests.get(file_url, timeout=30)
    response.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=extensao)
    tmp.write(response.content)
    tmp.close()
    return tmp.name


def transcrever_audio(caminho_arquivo: str) -> str:
    """Transcreve o áudio usando Whisper e retorna o texto."""
    segments, _ = whisper_model.transcribe(
        caminho_arquivo,
        language="pt",
        beam_size=5,
    )
    return " ".join(seg.text.strip() for seg in segments).strip()


def classificar_transcricao(transcricao: str) -> dict:
    """
    Envia a transcrição ao Ollama e interpreta a resposta em prefixo simples.

    Retorno:
    {
        "tipo":     "funcao" | "resposta",
        "valor":    nome da função ou texto da resposta
    }
    """
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": transcricao},
            ],
        )

        linha = response["message"]["content"].strip().splitlines()[0].strip()

        if linha.startswith("FUNCAO:"):
            funcao = linha.split("FUNCAO:", 1)[1].strip().lower()
            return {"tipo": "funcao", "valor": funcao}

        if linha.startswith("RESPOSTA:"):
            resposta = linha.split("RESPOSTA:", 1)[1].strip()
            return {"tipo": "resposta", "valor": resposta}

        # fallback: se o modelo não seguiu o formato, trata como resposta livre
        logger.warning("Formato inesperado do Ollama: %s", linha)
        return {"tipo": "resposta", "valor": linha}

    except Exception as e:
        logger.error("Erro na classificação Ollama: %s", e)
        return {"tipo": "funcao", "valor": "inicio"}


def processar_audio(bot, file_id: str) -> dict:
    """
    Pipeline completo: baixa, transcreve e classifica o áudio.

    Retorno:
    {
        "transcricao": str,
        "tipo":        "funcao" | "resposta",
        "valor":       str
    }
    """
    caminho_arquivo = None
    try:
        caminho_arquivo = baixar_audio(bot, file_id)
        transcricao = transcrever_audio(caminho_arquivo)
        classificacao = classificar_transcricao(transcricao)
        return {"transcricao": transcricao, **classificacao}
    finally:
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)