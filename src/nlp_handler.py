import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

PROMPT_TEMPLATE = (
    'Você é um assistente de vacinação do SUS.\n'
    'O usuário enviou a seguinte mensagem: "{mensagem}"\n\n'
    "Retorne APENAS um JSON no seguinte formato, sem nenhum texto adicional:\n"
    '{\n'
    '  "intencao": "<uma das intenções válidas>",\n'
    '  "parametros": { <parâmetros relevantes> }\n'
    '}\n\n'
     "Intenções válidas: agendar, vacinas_por_grupo, vacinas_por_idade, cobertura_estado,\n"
     "cobertura_municipio, postos_proximos, faq, encerrar, desconhecida.\n\n"
    "Se não conseguir identificar a intenção com certeza, use \"desconhecida\".\n"
)

INTENCOES_VALIDAS = {
    "agendar",
    "vacinas_por_grupo",
    "vacinas_por_idade",
    "cobertura_estado",
    "cobertura_municipio",
    "postos_proximos",
    "faq",
    "encerrar",
    "desconhecida",
}


def interpretar_mensagem(texto):
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": PROMPT_TEMPLATE.format(mensagem=texto),
            "stream": False,
            "format": "json",
        }
        response = requests.post(
            f"{OLLAMA_URL}/api/generate", json=payload, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "").strip()

        resultado = json.loads(raw)
        intencao = resultado.get("intencao", "desconhecida")

        if intencao not in INTENCOES_VALIDAS:
            intencao = "desconhecida"

        logger.info(f"Intenção: {intencao} | Parâmetros: {resultado.get('parametros', {})}")
        return {
            "intencao": intencao,
            "parametros": resultado.get("parametros", {}),
        }

    except (requests.ConnectionError, requests.Timeout):
        logger.warning("Ollama offline — retornando intenção desconhecida")
        return {"intencao": "desconhecida", "parametros": {}}

    except (json.JSONDecodeError, KeyError, Exception) as e:
        logger.error(f"Erro ao interpretar mensagem: {e}")
        return {"intencao": "desconhecida", "parametros": {}}
