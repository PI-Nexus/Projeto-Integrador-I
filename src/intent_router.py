import re
import logging
from datetime import datetime

from telebot import types

from src.scrap import scrap, formatar_mensagem_bot
from src.auxiliares import (
    definir_categoria_por_idade,
    converter_periodo_para_meses,
)
from src.scrap_cobertura import (
    buscar_cobertura_estado,
    buscar_cobertura_municipio,
)

logger = logging.getLogger(__name__)

GRUPOS_VALIDOS = {"crianca", "adolescente", "adulto", "idoso", "gestante"}


def rotear_intencao(bot, message, intencao_json, user_states):
    chat_id = message.chat.id
    try:
        intencao = intencao_json.get("intencao", "desconhecida")
        params = intencao_json.get("parametros", {})

        roteador = {
            "agendar": _agendar,
            "vacinas_por_grupo": _vacinas_por_grupo,
            "vacinas_por_idade": _vacinas_por_idade,
            "cobertura_estado": _cobertura_estado,
            "cobertura_municipio": _cobertura_municipio,
            "postos_proximos": _postos_proximos,
            "faq": _faq,
            "encerrar": _encerrar,
            "desconhecida": _desconhecida,
        }

        handler = roteador.get(intencao, _desconhecida)
        handler(bot, chat_id, message, params)

    except Exception as e:
        logger.error(f"Erro no roteamento de intenção: {e}", exc_info=True)
        _desconhecida(bot, chat_id, message, {})


def _agendar(bot, chat_id, message, params):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Grupo', 'Idade', 'Voltar ao Menu Principal')
    bot.send_message(
        chat_id,
        "Para agendar vacinas, primeiro preciso saber quais você precisa. "
        "Como deseja pesquisar?",
        reply_markup=markup,
    )


def _vacinas_por_grupo(bot, chat_id, message, params):
    grupo = str(params.get("grupo", "")).lower().strip()

    if grupo not in GRUPOS_VALIDOS:
        bot.send_message(
            chat_id,
            "Grupo não reconhecido. Use: criança, adolescente, adulto, idoso ou gestante.",
        )
        return

    dados = scrap(grupo)
    if not dados:
        bot.send_message(chat_id, f"Nenhuma vacina encontrada para o grupo {grupo}.")
        return

    resposta = formatar_mensagem_bot(dados)
    bot.send_message(chat_id, resposta, parse_mode="Markdown")


def _vacinas_por_idade(bot, chat_id, message, params):
    idade = _extrair_idade(params)

    if idade is None:
        bot.send_message(
            chat_id,
            "Informe a idade ou a data de nascimento da pessoa (ex: '3 anos' ou '10/03/2022').",
        )
        return

    categoria = definir_categoria_por_idade(idade)
    dados = scrap(categoria)

    if not dados:
        bot.send_message(chat_id, f"Nenhuma vacina encontrada para esta faixa etária.")
        return

    if idade < 12:
        idade_meses = idade * 12
        dados = [
            v
            for v in dados
            if converter_periodo_para_meses(v["periodo"]) >= idade_meses
        ]

    if not dados:
        bot.send_message(chat_id, f"Nenhuma vacina pendente para esta idade.")
        return

    resposta = formatar_mensagem_bot(dados)
    bot.send_message(chat_id, resposta, parse_mode="Markdown")


def _extrair_idade(params):
    if "idade" in params and params["idade"]:
        nums = re.findall(r"\d+", str(params["idade"]))
        if nums:
            return int(nums[0])

    if "data" in params and params["data"]:
        for fmt in ["%d/%m/%Y", "%Y-%m-%d"]:
            try:
                nasc = datetime.strptime(str(params["data"]), fmt)
                hoje = datetime.now()
                return hoje.year - nasc.year - (
                    (hoje.month, hoje.day) < (nasc.month, nasc.day)
                )
            except ValueError:
                continue

    return None


def _cobertura_estado(bot, chat_id, message, params):
    estado = str(params.get("estado", "")).strip().upper()

    if not estado or len(estado) != 2:
        bot.send_message(chat_id, "Informe a sigla do estado (ex: SP).")
        return

    bot.send_message(chat_id, "🔎 Buscando dados... aguarde ⏳")
    resposta = buscar_cobertura_estado(estado)
    bot.send_message(chat_id, resposta, parse_mode="HTML")


def _cobertura_municipio(bot, chat_id, message, params):
    estado = str(params.get("estado", "")).strip().upper()
    municipio = str(params.get("municipio", "")).strip()

    if not estado or not municipio:
        bot.send_message(chat_id, "Informe o estado e o município desejado.")
        return

    bot.send_message(chat_id, "🔎 Buscando dados... aguarde ⏳")
    resposta = buscar_cobertura_municipio(estado, municipio)
    bot.send_message(chat_id, resposta, parse_mode="HTML")


def _postos_proximos(bot, chat_id, message, params):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_gps = types.KeyboardButton(
        "📍 Compartilhar minha localização atual", request_location=True
    )
    markup.add(btn_gps, "Voltar ao Menu Principal")
    bot.send_message(
        chat_id,
        "Compartilhe sua localização para encontrar as UBS mais próximas:",
        reply_markup=markup,
    )


def _faq(bot, chat_id, message, params):
    tema = str(params.get("tema", "")).lower()

    if "documento" in tema:
        bot.send_message(
            chat_id,
            "📋 Documentos Necessários: Documento com Foto e Caderneta de Vacinação.",
        )
    elif "reaç" in tema or "reac" in tema:
        bot.send_message(
            chat_id, "🌡️ Reações Comuns: Febre Leve e Cansaço (duração de 1 a 3 dias)."
        )
    else:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add("Documentos Necessários", "Reações Comuns", "Voltar ao Menu Principal")
        bot.send_message(chat_id, "📌 Escolha um tópico de FAQ:", reply_markup=markup)


def _encerrar(bot, chat_id, message, params):
    bot.send_message(
        chat_id, "✅ Atendimento finalizado!", reply_markup=types.ReplyKeyboardRemove()
    )


def _desconhecida(bot, chat_id, message, params):
    bot.send_message(
        chat_id,
        "Não entendi. Quer usar o menu?",
        reply_markup=_menu_markup(),
    )


def _menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Início", "Vacinas", "Cobertura Vacinal", "Unidades próximas", "FAQ")
    return markup
