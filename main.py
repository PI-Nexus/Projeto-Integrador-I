import threading
import telebot
import os
from telebot import types
from datetime import datetime
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardRemove
from flask import Flask
from src.auxiliares import plural
from src.scrap import formatar_mensagem_bot, scrap
import shutil

load_dotenv()

TOKEN = os.getenv('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN)

# --- HANDLERS PRINCIPAIS ---

@bot.message_handler(commands=['start', 'help'])
def comandos(msg):
    # Se o usuário digitar /help, ele cai direto no menu de FAQ
    if msg.text == '/help':
        faq_menu(msg)
    else:
        servicos(msg)

def servicos(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # Mudança: 'Help' virou 'FAQ'
    markup.add('Início', 'Vacinas', 'FAQ')
    bot.send_message(msg.chat.id, 'Olá, sou o seu assistente virtual! Selecione uma opção abaixo.', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg,
                 "Você está no início do assistente virtual! Estou aqui para te ajudar a encontrar as vacinas disponíveis para você. Selecione 'Vacinas' para começar.")

# --- LÓGICA DO NOVO FAQ ---

@bot.message_handler(func=lambda msg: msg.text == "FAQ")
def faq_menu(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # Sub-botões de dúvidas
    markup.add('Onde me vacinar?', 'Documentos necessários', 'Reações comuns', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "📌 *Dúvidas Frequentes sobre Vacinação*\nEscolha um tópico abaixo para saber mais:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text in ['Onde me vacinar?', 'Documentos necessários', 'Reações comuns', 'Voltar ao Menu Principal'])
def faq_respostas(msg):
    if msg.text == 'Onde me vacinar?':
        bot.send_message(msg.chat.id, "📍 Você pode se vacinar em qualquer Unidade Básica de Saúde (UBS) ou Posto de Saúde. Verifique o site da prefeitura de São José dos Campos para consultar locais e horários específicos.")
    
    elif msg.text == 'Documentos necessários':
        bot.send_message(msg.chat.id, "📄 Os documentos padrão são:\n1. Documento com foto (RG/CNH)\n2. CPF\n3. Cartão do SUS\n4. Caderneta de Vacinação (se tiver).")
    
    elif msg.text == 'Reações comuns':
        bot.send_message(msg.chat.id, "💉 É normal sentir dor leve no braço, um pouco de febre ou cansaço após algumas vacinas. Isso indica que seu corpo está criando proteção. Se os sintomas forem graves, procure um médico.")
    
    elif msg.text == 'Voltar ao Menu Principal':
        servicos(msg)

# --- FLUXO DE VACINAS ---

@bot.message_handler(func=lambda msg: msg.text == "Continuar")
def menu(msg):
    servicos(msg)

@bot.message_handler(func=lambda msg: msg.text == "Encerrar")
def finalizar_servico(msg):
    final_message="✅ Atendimento finalizado!\nCuide da sua saúde e mantenha sua vacinação em dia 💉\nAté logo! 👋"
    bot.send_message(msg.chat.id, final_message, reply_markup=ReplyKeyboardRemove())
    try:
        if os.path.exists('data'):
            shutil.rmtree('data')
    except Exception as e:
        print(f'Não foi possível apagar o diretório: {e}')

@bot.message_handler(func=lambda msg: msg.text == "Vacinas")
def filtrar_pesquisa(msg):
    markup=types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Grupo', 'Idade')
    bot.send_message(msg.chat.id, "Como deseja filtrar sua pesquisa?", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Idade")
def pegar_idade(msg):
    bot.send_message(msg.chat.id, "Informe a data de nascimento da pessoa no formato DD/MM/AAAA.", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, processar_dados)

def processar_dados(msg):
    sub_faixa = []
    data_texto = msg.text

    faixa_crianca_meses={'Ao nascer':(0,59),'2 meses':(60,89) , '3 meses':(90,119),'4 meses':(120,149),'5 meses':(150,179),'6 meses':(180,209) ,'6 a 8 meses':(180,240),'7 meses':(210,239), '9 meses':(270,299), '12 meses':(360,389),'15 meses':(450,479)}
    faixa_crianca_anos={ '4 anos':(48,59), '5 anos':(60,71),'A partir dos 7 anos':(84,167), '9 a 14 anos':(108,179)}
    faixa_adolescente={'9 a 14 anos':(9,14), '10 a 14 anos':(10,14), '11 a 14 anos':(11,14), '10 a 24 anos':(10,24)}

    try:
        data_nascimento = datetime.strptime(data_texto, "%d/%m/%Y")
        hoje = datetime.now()

        idadeAnos = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        idadeDias = (hoje - data_nascimento).days
        idadeMes = int(idadeDias / 30)

        if idadeMes <= 15:
            id_site = 'crianca'
            for chave, valor in faixa_crianca_meses.items():
                if valor[0] <= idadeDias <= valor[1]:
                    sub_faixa.append(chave)

        elif idadeMes > 15 and idadeAnos <= 14:
            id_site = "crianca"
            for chave, valor in faixa_crianca_anos.items():
                if valor[0] <= idadeMes <= valor[1]:
                    sub_faixa.append(chave)
            if len(sub_faixa) == 0:
                sub_faixa.append(list(faixa_crianca_anos.keys())[0])

        elif 14 < idadeAnos <= 24:
            id_site = "adolescente"
            for chave, valor in faixa_adolescente.items():
                if valor[0] <= idadeAnos <= valor[1]:
                    sub_faixa.append(chave)

        elif 25 <= idadeAnos <= 59:
            id_site = "adulto"
        else:
            id_site = "idoso"

        dados_vacinas = scrap(id_site, sub_faixa)
        mensagem_final = formatar_mensagem_bot(dados_vacinas)
        faixa_amigavel = dados_vacinas[0]['grupo']

        bot.send_message(msg.chat.id,
                         f"✅ Grupo: {faixa_amigavel} ({idadeAnos if idadeAnos >= 1 else idadeMes} {plural('ano','anos',idadeAnos) if idadeAnos>=1 else plural('mês','meses',idadeMes)}).\n⌛ Buscando informações oficiais...")

        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")
        servico_final(msg)

    except ValueError:
        bot.reply_to(msg, "⚠️ Formato inválido! Use DD/MM/AAAA.")

@bot.message_handler(func=lambda msg: msg.text == "Grupo")
def grupos(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add("Crianca", "Adolescente", "Adulto", "Idoso", "Gestante")
    sent_msg = bot.send_message(msg.chat.id, 'Informe o grupo para pesquisa.', reply_markup=markup)
    bot.register_next_step_handler(sent_msg, enviar_grupos)

def enviar_grupos(msg):
    id_site = msg.text.lower()
    try:
        dados_vacinais = scrap(id_site)
        mensagem_final = formatar_mensagem_bot(dados_vacinais)
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        servico_final(msg)
    except Exception:
        bot.reply_to(msg, 'Não encontramos dados para esse grupo.')

def servico_final(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Encerrar', 'Continuar')
    bot.send_message(msg.chat.id, 'Sua pesquisa chegou ao fim. Deseja continuar?', reply_markup=markup)

# --- SERVIDOR FLASK ---

app = Flask('')
@app.route('/')
def home():
    return "Bot Gotinha está online ! ✅"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run)
    t.start()
    print("Bot iniciando...")
    bot.infinity_polling()