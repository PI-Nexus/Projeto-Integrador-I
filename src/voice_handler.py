import os
import logging
import whisper
from pydub import AudioSegment

logger = logging.getLogger(__name__)

_model = None

def _carregar_modelo():
    global _model
    if _model is None:
        logger.info("Carregando modelo Whisper 'base'...")
        _model = whisper.load_model("base")
    return _model

def transcrever_audio(caminho_ogg):
    caminho_wav = caminho_ogg.replace(".ogg", ".wav")
    try:
        audio = AudioSegment.from_ogg(caminho_ogg)
        audio.export(caminho_wav, format="wav")

        modelo = _carregar_modelo()
        resultado = modelo.transcribe(caminho_wav, language="pt", fp16=False)
        texto = resultado["text"].strip()

        logger.info(f"Transcrição concluída: {texto[:50]}...")
        return texto

    except Exception as e:
        logger.error(f"Erro na transcrição de áudio: {e}")
        return None

    finally:
        for f in [caminho_ogg, caminho_wav]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
