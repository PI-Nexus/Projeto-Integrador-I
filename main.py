# Bibliotecas padrão
import os
import threading
from datetime import datetime
import re

# Bibliotecas externas
import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove
from dotenv import load_dotenv
from flask import Flask

# Módulos internos
from src.scrap import formatar_mensagem_bot, scrap
from src.scrap_cobertura import (
    buscar_cobertura_estado,
    buscar_cobertura_municipio,
    calcular_media_estados,
    baixar_e_tratar_dados,
)
from src.buscar_postos import buscar_postos_proximos, threading_search, start_drivers
import src.notify as notify
from src.auxiliares import (
    gerar_botoes_vacinas,
    calcular_data_alvo,
    definir_categoria_por_idade,
    converter_periodo_para_meses,
    validar_data,
)

# 1. Configurações Iniciais
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN)

user_states = {}

# 2. Servidor Flask
app = Flask('')

@app.route('/')
def home():
    return "Bot Gotinha está online ! ✅"

# --- HANDLERS DE COMANDO INICIAIS ---
@bot.message_handler(commands=['start', 'help'])
def comandos(msg):
    threading.Thread(target=baixar_e_tratar_dados).start()
    servicos(msg)

def servicos(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        'Início',
        'Vacinas',
        'Cobertura Vacinal',
        'Unidades próximas',
        'FAQ'
    )
    bot.send_message(msg.chat.id, 'Olá! Eu sou o Assistente Gotinha. Como posso te ajudar?', reply_markup=markup)

# --- HANDLERS ORIGINAIS COM BOTÕES ---
@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg, "Você está no início! Selecione 'Vacinas' ou consulte as UBS próximas pelo GPS.")

# DUPLICAÇÃO PARA COMANDOS DE VOZ
@bot.message_handler(commands=['inicio', 'start_voice'])
def resposta_inicio_voice(msg):
    bot.reply_to(msg, "Você está no início! Selecione 'Vacinas' ou consulte as UBS próximas pelo GPS. (via comando de voz)")

# --- Cobertura Vacinal ---
regioes = {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"]
}

@bot.message_handler(func=lambda msg: msg.text == "Cobertura Vacinal")
def menu_cobertura(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        "Dashboard",
        "Estado",
        "Município",
        "Ranking de Estados 🇧🇷",
        "Voltar ao Menu Principal",
    )
    bot.send_message(msg.chat.id, "Como deseja consultar a cobertura vacinal?", reply_markup=markup)

# Duplicado por comando de voz
@bot.message_handler(commands=['voice', 'audio'])
def menu_cobertura_voice(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        "Dashboard",
        "Estado",
        "Município",
        "Ranking de Estados 🇧🇷",
        "Voltar ao Menu Principal",
    )
    bot.send_message(msg.chat.id, "Como deseja consultar a cobertura vacinal? (via comando de voz)", reply_markup=markup)

# Cobertura por estado
@bot.message_handler(func=lambda msg: msg.text == "Estado")
def cobertura_por_estado(msg):
    user_states[msg.chat.id] = {"modo_cobertura": "estado"}
    escolher_regiao(msg)

@bot.message_handler(commands=['estado', 'uf'])
def cobertura_por_estado_voice(msg):
    user_states[msg.chat.id] = {"modo_cobertura": "estado"}
    escolher_regiao(msg)

# Cobertura por município
@bot.message_handler(func=lambda msg: msg.text == "Município")
def cobertura_por_municipio_inicio(msg):
    user_states[msg.chat.id] = {"modo_cobertura": "municipio"}
    escolher_regiao_municipio(msg)

@bot.message_handler(commands=['municipio', 'cidade'])
def cobertura_por_municipio_voice(msg):
    user_states[msg.chat.id] = {"modo_cobertura": "municipio"}
    escolher_regiao_municipio(msg)

# Dashboard
@bot.message_handler(func=lambda msg: msg.text == "Dashboard")
def dashboard(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Voltar ao Menu Principal','Encerrar')
    link = os.getenv('LINK_POWERBI')
    bot.send_message(msg.chat.id, f"📊 <b>Dashboard de Cobertura Vacinal</b> — <a href='{link}'>Acessar</a>",
                     reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['dashboard'])
def dashboard_voice(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Voltar ao Menu Principal','Encerrar')
    link = os.getenv('LINK_POWERBI')
    bot.send_message(msg.chat.id, f"📊 <b>Dashboard de Cobertura Vacinal</b> — <a href='{link}'>Acessar</a> (via comando de voz)",
                     reply_markup=markup, parse_mode="HTML")

# Ranking de estados
@bot.message_handler(func=lambda msg: msg.text == "Ranking de Estados 🇧🇷")
def cobertura_ranking(msg):
    bot.send_message(msg.chat.id, "🔎 Calculando ranking nacional... aguarde ⏳")
    resposta = calcular_media_estados()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Realizar nova consulta", "Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['ranking'])
def cobertura_ranking_voice(msg):
    bot.send_message(msg.chat.id, "🔎 Calculando ranking nacional... aguarde ⏳ (via comando de voz)")
    resposta = calcular_media_estados()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Realizar nova consulta", "Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

# Voltar ao menu principal
@bot.message_handler(func=lambda msg: msg.text == "Voltar ao Menu Principal")
def voltar(msg):
    servicos(msg)

@bot.message_handler(commands=['menu', 'inicio_voice'])
def voltar_voice(msg):
    servicos(msg)

# Unidades próximas
@bot.message_handler(func=lambda msg: msg.text == "Unidades próximas")
def pedir_localizacao(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_gps = types.KeyboardButton("📍 Compartilhar minha localização atual", request_location=True)
    markup.add(btn_gps, "Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, "Clique no botão abaixo para encontrar as UBS mais próximas.", reply_markup=markup)

@bot.message_handler(commands=['postos', 'unidades'])
def pedir_localizacao_voice(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_gps = types.KeyboardButton("📍 Compartilhar minha localização atual", request_location=True)
    markup.add(btn_gps, "Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, "Clique no botão abaixo para encontrar as UBS mais próximas (via comando de voz).", reply_markup=markup)

# FAQ
@bot.message_handler(func=lambda msg: msg.text == "FAQ")
def faq_menu(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Documentos Necessários', 'Reações Comuns', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "📌 *Dúvidas Frequentes*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['faq'])
def faq_menu_voice(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Documentos Necessários', 'Reações Comuns', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "📌 *Dúvidas Frequentes* (via comando de voz)", reply_markup=markup, parse_mode="Markdown")

# --- Replicar todos os outros menus e fluxos do código original ---
# (Vacinas, Idade, Grupo, Processamento de datas, Callback queries etc.)
# Para cada handler original com func=lambda, criar duplicado usando:
# @bot.message_handler(commands=['nome_comando', 'outro_comando'])

# Exemplo genérico para Vacinas
@bot.message_handler(func=lambda msg: msg.text == "Vacinas")
def filtrar_pesquisa(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Grupo', 'Idade', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "Como deseja pesquisar?", reply_markup=markup)

@bot.message_handler(commands=['vacinas'])
def filtrar_pesquisa_voice(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Grupo', 'Idade', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "Como deseja pesquisar? (via comando de voz)", reply_markup=markup)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    bot.remove_webhook()
    port = int(os.environ.get("PORT", 8080))
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False))
    t.daemon = True
    t.start()

    t_notifica = threading.Thread(target=notify.loop_notificacao, args=(bot,))
    t_notifica.daemon = True
    t_notifica.start()

    print("Bot Gotinha Ativado com Localização! 🚀")
    bot.infinity_polling()