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
from src.buscar_postos import buscar_postos_proximos, retorno_link_maps

# 1. Configurações Iniciais
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# 2. Definição do Servidor Flask
app = Flask('')

@app.route('/') 
def home():
    return "Bot Gotinha está online ! ✅"

# --- HANDLERS DE INTERFACE ---

@bot.message_handler(commands=['start', 'help'])
def comandos(msg):
    servicos(msg)

def servicos(msg):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('Início', callback_data='inicio'),
        types.InlineKeyboardButton('Vacinas', callback_data='vacinas'),
        types.InlineKeyboardButton('Cobertura Vacinal', callback_data='cobertura_vacinal'),
        types.InlineKeyboardButton('Unidades próximas', callback_data='unidades_proximas'),
        types.InlineKeyboardButton('FAQ', callback_data='faq'),
    )
    bot.send_message(msg.chat.id, 'Olá! Eu sou o Assistente Gotinha. Como posso te ajudar?', reply_markup=markup)

# --- CALLBACKS DOS BOTÕES INLINE ---

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id)  # Remove o "carregando" do botão
    msg = call.message

    if call.data == 'inicio':
        bot.edit_message_text(
            "Você está no início! Selecione 'Vacinas' ou consulte as UBS próximas pelo GPS.",
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reply_markup=_markup_voltar_menu()
        )

    elif call.data == 'cobertura_vacinal':
        bot.edit_message_text(
            "Digite a sigla do estado (ex: SP):",
            chat_id=msg.chat.id,
            message_id=msg.message_id
        )
        bot.register_next_step_handler(msg, processar_estado)

    elif call.data == 'consultar_outro_estado':
        bot.edit_message_text(
            "Digite a sigla do estado (ex: SP):",
            chat_id=msg.chat.id,
            message_id=msg.message_id
        )
        bot.register_next_step_handler(msg, processar_estado)

    elif call.data == 'unidades_proximas':
        # Localização ainda precisa de ReplyKeyboard (limitação do Telegram)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        btn_gps = types.KeyboardButton("📍 Compartilhar minha localização atual", request_location=True)
        reply_markup.add(btn_gps)
        bot.send_message(
            msg.chat.id,
            "Para encontrar as UBS mais próximas, clique no botão abaixo para enviar seu GPS.",
            reply_markup=reply_markup
        )

    elif call.data == 'vacinas':
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton('Grupo', callback_data='grupo'),
            types.InlineKeyboardButton('Idade', callback_data='idade'),
            types.InlineKeyboardButton('Voltar ao Menu Principal', callback_data='menu_principal'),
        )
        bot.edit_message_text(
            "Como deseja pesquisar?",
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reply_markup=markup
        )

    elif call.data == 'idade':
        bot.edit_message_text(
            "Informe a data de nascimento (DD/MM/AAAA).",
            chat_id=msg.chat.id,
            message_id=msg.message_id
        )
        bot.register_next_step_handler(msg, processar_dados)

    elif call.data == 'grupo':
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton('Crianca', callback_data='grupo_crianca'),
            types.InlineKeyboardButton('Adolescente', callback_data='grupo_adolescente'),
            types.InlineKeyboardButton('Adulto', callback_data='grupo_adulto'),
            types.InlineKeyboardButton('Idoso', callback_data='grupo_idoso'),
            types.InlineKeyboardButton('Gestante', callback_data='grupo_gestante'),
        )
        bot.edit_message_text(
            'Selecione o grupo:',
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reply_markup=markup
        )
        
    elif call.data.startswith('grupo_'):
        id_site = call.data.replace('grupo_', '')
        try:
            dados_vacinais = scrap(id_site)
            mensagem_final = formatar_mensagem_bot(dados_vacinais)
            bot.edit_message_text(
                mensagem_final,
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                parse_mode="Markdown"
            )
            _enviar_servico_final(msg.chat.id)
        except Exception:
            bot.edit_message_text(
                'Não encontramos dados.',
                chat_id=msg.chat.id,
                message_id=msg.message_id
            )

    elif call.data == 'faq':
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton('Documentos necessários', callback_data='faq_documentos'),
            types.InlineKeyboardButton('Reações comuns', callback_data='faq_reacoes'),
            types.InlineKeyboardButton('Voltar ao Menu Principal', callback_data='menu_principal'),
        )
        bot.edit_message_text(
            "📌 *Dúvidas Frequentes*",
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif call.data in ('menu_principal', 'continuar'):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton('Início', callback_data='inicio'),
            types.InlineKeyboardButton('Vacinas', callback_data='vacinas'),
            types.InlineKeyboardButton('Cobertura Vacinal', callback_data='cobertura_vacinal'),
            types.InlineKeyboardButton('Unidades próximas', callback_data='unidades_proximas'),
            types.InlineKeyboardButton('FAQ', callback_data='faq'),
        )
        bot.edit_message_text(
            'Olá! Eu sou o Assistente Gotinha. Como eu posso te ajudar?',
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reply_markup=markup
        )

    elif call.data == 'encerrar':
        bot.edit_message_text(
            "✅ Atendimento finalizado!",
            chat_id=msg.chat.id,
            message_id=msg.message_id
        )

# --- FLUXO DE COBERTURA VACINAL ---

def processar_estado(msg):
    estado = msg.text.strip().upper()
    bot.send_message(msg.chat.id, "🔎 Buscando dados atualizados... aguarde um instante ⏳")
    resposta = buscar_cobertura_estado(estado)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Consultar outro estado", callback_data="consultar_outro_estado"),
        types.InlineKeyboardButton("Continuar", callback_data="continuar"),
        types.InlineKeyboardButton("Voltar ao Menu Principal", callback_data="menu_principal"),
    )
    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="Markdown")

# --- FLUXO DE LOCALIZAÇÃO ---

@bot.message_handler(content_types=['location'])
def tratar_localizacao(msg):
    try:
        lat = msg.location.latitude
        lon = msg.location.longitude
        postos_proximos = buscar_postos_proximos(lat, lon)

        message = ''
        for posto in postos_proximos:
            print(posto)
            maps = retorno_link_maps(posto)
            message += f'\n<a href="{maps}">{posto["nome"]}</a>\n'

        bot.send_message(msg.chat.id, message, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        _enviar_servico_final(msg.chat.id)

    except Exception as e:
        print(f"Erro GPS: {e}")
        bot.send_message(msg.chat.id, "⚠️ Erro ao consultar o portal de saúde.", reply_markup=ReplyKeyboardRemove())

# --- FLUXO DE VACINAS POR IDADE ---

def processar_dados(msg):
    sub_faixa = []
    data_texto = msg.text
    try:
        data_nascimento = datetime.strptime(data_texto, "%d/%m/%Y")
        hoje = datetime.now()
        idadeAnos = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        
        id_site = "adulto" if idadeAnos >= 18 else "crianca"
        
        dados_vacinas = scrap(id_site, sub_faixa)
        mensagem_final = formatar_mensagem_bot(dados_vacinas)
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")
        _enviar_servico_final(msg.chat.id)
    except Exception as e:
        bot.reply_to(msg, "⚠️ Formato inválido ou erro no processamento.")

# --- HELPERS ---

def _markup_voltar_menu() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('Voltar ao Menu Principal', callback_data='menu_principal'))
    return markup

def _enviar_servico_final(chat_id: int):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('Encerrar', callback_data='encerrar'),
        types.InlineKeyboardButton('Continuar', callback_data='continuar'),
    )
    bot.send_message(chat_id, 'Deseja realizar outra consulta?', reply_markup=markup)

# --- EXECUÇÃO ---

if __name__ == "__main__":
    bot.remove_webhook()
    
    port = int(os.environ.get("PORT", 8080))
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False))
    t.daemon = True
    t.start()
    
    print("Bot Gotinha Ativado com Localização! 🚀")
    bot.infinity_polling()
