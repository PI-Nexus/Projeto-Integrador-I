import threading
import telebot
import os
from telebot import types
from datetime import datetime
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardRemove
from flask import Flask

# Importações das suas funções internas
from src.scrap import formatar_mensagem_bot, scrap
from src.scrap_cnes import buscar_ubs_cnes 
from geopy.geocoders import Nominatim       
import shutil
import src.buscar_postos
from src.scrap_cobertura import buscar_cobertura_estado
from src.buscar_postos import buscar_postos_proximos,retorno_link_maps

# 1. Configurações Iniciais
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# 2. Definição do Servidor Flask (Precisa estar aqui no escopo global)
app = Flask('')

@app.route('/')
def home():
    return "Bot Gotinha está online ! ✅"

# --- HANDLERS DE INTERFACE ---

@bot.message_handler(commands=['start', 'help'])
def comandos(msg):
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

@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg, "Você está no início! Selecione 'Vacinas' ou consulte as UBS próximas pelo GPS.")

# --- FLUXO DE COBERTURA VACINAL ---
@bot.message_handler(func=lambda msg: msg.text == "Cobertura Vacinal")
def pedir_estado(msg):
    bot.send_message(msg.chat.id, "Digite a sigla do estado (ex: SP):")
    bot.register_next_step_handler(msg, processar_estado)

def processar_estado(msg):
    estado = msg.text.strip().upper()

    bot.send_message(msg.chat.id, "🔎 Buscando dados atualizados... aguarde um instante ⏳")

    resposta = buscar_cobertura_estado(estado)

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Consultar outro estado", "Continuar", "Voltar ao Menu Principal")

    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="Markdown")

# --- CONSULTAR OUTRO ESTADO ---
@bot.message_handler(func=lambda msg: msg.text == "Consultar outro estado")
def repetir_consulta(msg):
    bot.send_message(msg.chat.id, "Digite a sigla do estado (ex: SP):")
    bot.register_next_step_handler(msg, processar_estado)
    
# --- FLUXO DE LOCALIZAÇÃO (DESTAQUE DA SPRINT) ---

@bot.message_handler(func=lambda msg: msg.text == "Unidades próximas")
def pedir_localizacao(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_gps = types.KeyboardButton("📍 Compartilhar minha localização atual", request_location=True)
    markup.add(btn_gps, "Voltar ao Menu Principal")
    
    bot.send_message(msg.chat.id, 
        "Para encontrar as UBS mais próximas, clique no botão abaixo para enviar seu GPS.", 
        reply_markup=markup)

@bot.message_handler(content_types=['location'])
def tratar_localizacao(msg):
    lat = msg.location.latitude
    lon = msg.location.longitude
    #Mensagem de espera
    bot.send_message(
    msg.chat.id,
    "📍 Localização recebida.\nEstou buscando os postos mais próximos de você... aguarde alguns segundos."
)
    postos_proximos = buscar_postos_proximos(lat, lon)

    # Retorno das coordenadas em formato de lista/texto monoespaçado
    message=''
    for posto in postos_proximos:
        print(posto)
        maps = retorno_link_maps(posto)
        message += f'\n<a href="{maps}">{posto["nome"]}</a>\n'

    bot.send_message(msg.chat.id, message, parse_mode="HTML")

    try:
        lat = msg.location.latitude
        lon = msg.location.longitude
        postos_proximos = buscar_postos_proximos(lat, lon)

        # Retorno das coordenadas em formato de lista/texto monoespaçado
        message = ''
        for posto in postos_proximos:
            print(posto)
            maps = retorno_link_maps(posto)
            message += f'\n<a href="{maps}">{posto["nome"]}</a>\n'

        bot.send_message(msg.chat.id, message, parse_mode="HTML")

    except Exception as e:
        print(f"Erro GPS: {e}")
        bot.send_message(msg.chat.id, "⚠️ Erro ao consultar o portal de saúde.")

# --- FLUXO DE VACINAS ---

@bot.message_handler(func=lambda msg: msg.text == "Vacinas")
def filtrar_pesquisa(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Grupo', 'Idade', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "Como deseja pesquisar?", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Idade")
def pegar_idade(msg):
    bot.send_message(msg.chat.id, "Informe a data de nascimento (DD/MM/AAAA).", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, processar_dados)

def processar_dados(msg):
    # Mantendo sua lógica de cálculo de idade original
    sub_faixa = []
    data_texto = msg.text
    try:
        data_nascimento = datetime.strptime(data_texto, "%d/%m/%Y")
        hoje = datetime.now()
        idadeAnos = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        
        # Simplificação para o exemplo, use suas faixas de meses aqui
        id_site = "adulto" if idadeAnos >= 18 else "crianca"
        
        dados_vacinas = scrap(id_site, sub_faixa)
        mensagem_final = formatar_mensagem_bot(dados_vacinas)
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")
        servico_final(msg)
    except Exception as e:
        bot.reply_to(msg, "⚠️ Formato inválido ou erro no processamento.")

@bot.message_handler(func=lambda msg: msg.text == "Grupo")
def grupos(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Crianca", "Adolescente", "Adulto", "Idoso", "Gestante")
    sent_msg = bot.send_message(msg.chat.id, 'Selecione o grupo:', reply_markup=markup)
    bot.register_next_step_handler(sent_msg, enviar_grupos)

def enviar_grupos(msg):
    id_site = msg.text.lower()
    try:
        dados_vacinais = scrap(id_site)
        mensagem_final = formatar_mensagem_bot(dados_vacinais)
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")
        servico_final(msg)
    except Exception:
        bot.reply_to(msg, 'Não encontramos dados.')

# --- FAQ E ENCERRAMENTO ---

@bot.message_handler(func=lambda msg: msg.text == "FAQ")
def faq_menu(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Documentos necessários', 'Reações comuns', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "📌 *Dúvidas Frequentes*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "Voltar ao Menu Principal")
def voltar(msg):
    servicos(msg)

@bot.message_handler(func=lambda msg: msg.text == "Continuar")
def continuar(msg):
    servicos(msg)

@bot.message_handler(func=lambda msg: msg.text == "Encerrar")
def finalizar_servico(msg):
    bot.send_message(msg.chat.id, "✅ Atendimento finalizado!", reply_markup=ReplyKeyboardRemove())

def servico_final(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Encerrar', 'Continuar')
    bot.send_message(msg.chat.id, 'Deseja realizar outra consulta?', reply_markup=markup)

# --- EXECUÇÃO ---

if __name__ == "__main__":
    bot.remove_webhook()
    
    # Thread do Flask usando a variável 'app' definida no topo
    port = int(os.environ.get("PORT", 8080))
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False))
    t.daemon = True
    t.start()
    
    print("Bot Gotinha Ativado com Localização! 🚀")
    bot.infinity_polling()