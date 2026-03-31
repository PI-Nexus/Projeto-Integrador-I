import threading
from flask import Flask
import os
import telebot
from telebot import types
from datetime import datetime
from dotenv import load_dotenv
from src.auxiliares import plural
from src.scrap import formatar_mensagem_bot,scrap

load_dotenv()

TOKEN = os.getenv('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN)

# --- HANDLERS ---

@bot.message_handler(commands=['start', 'help'])
def start(msg: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Início', 'Vacinas', 'Help')
    bot.send_message(msg.chat.id, 'Olá, sou o seu assistente virtual! Selecione uma opção abaixo.', reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg,
                 "Você está no início do assistente virtual! Estou aqui para te ajudar a encontrar as vacinas disponíveis para você. Selecione 'Vacinas' para começar.")


@bot.message_handler(func=lambda msg: msg.text == "Help")
def resposta_help(msg):
    bot.reply_to(msg, "Para obter ajuda, acesse: \nhttps://LinkDoSite.")
    # Obs: fazer um site simples em html/css/js para melhorar a experiencia do usuário e suprir dúvidas

@bot.message_handler(func=lambda msg: msg.text == "Vacinas")
def pedir_modelo_pesquisa(msg):
    markup=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
    markup.add('Grupo','Idade')
    bot.send_message(msg.chat.id,"Como deseja filtrar sua pesquisa ? ",reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Idade")
def pedir_data_nascimento(msg):
    sent_msg = bot.reply_to(msg, "Informe a data de nascimento da pessoa no formato DD/MM/AAAA.")
    bot.register_next_step_handler(sent_msg, processar_data)

def processar_data(msg):
    sub_faixa =[]
    data_texto = msg.text

    faixa_crianca_meses={'Ao nascer':(0,59),'2 meses':(60,89) , '3 meses':(90,119),'4 meses':(120,149),'5 meses':(150,179),'6 meses':(180,209) ,'6 a 8 meses':(180,240),'7 meses':(210,239), '9 meses':(270,299), '12 meses':(360,389),'15 meses':(450,479)} #tuplas mapeadas em dias
    faixa_crianca_anos={ '4 anos':(48,59), '5 anos':(60,71),'A partir dos 7 anos':(84,167), '9 a 14 anos':(108,179)} #tuplas mapeadas em meses
    faixa_adolescente={'9 a 14 anos':(9,14), '10 a 14 anos':(10,14), '11 a 14 anos':(11,14), '10 a 24 anos':(10,24)} #tuplas mapeandas em anos

    try:
        data_nascimento = datetime.strptime(data_texto, "%d/%m/%Y")
        hoje = datetime.now()

        idadeAnos= hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        idadeDias=(hoje-data_nascimento).days
        idadeMes=int(idadeDias/30)

        # --- Mapeamento para o Scraping ---

        if idadeMes<=15:
            id_site='crianca'
            for chave,valor in faixa_crianca_meses.items():  # confere se está  no intervalo da tupla de sub faixas
                minimo=valor[0]
                maximo=valor[1]
                if minimo <= idadeDias <= maximo:
                    sub_faixa.append(chave)

        elif idadeMes>15 and idadeAnos<=14:
            id_site = "crianca"
            for chave, valor in faixa_crianca_anos.items():
                minimo=valor[0]
                maximo=valor[1]
                if minimo<=idadeMes<=maximo:
                    sub_faixa.append(chave)
            if len(sub_faixa)==0:
                sub_faixa.append(list(faixa_crianca_anos.keys())[0]) #  retorna o primeiro elemento de faixa_crianca_anos (casos entre 15 meses e 4 anos seriam nulos ))

        elif 14<idadeAnos<= 24:
            id_site = "adolescente"
            # maiores de 14 recebem somente faixa de 10 a 24 anos
            for chave, valor in faixa_adolescente.items():
                minimo = valor[0]
                maximo = valor[1]
                if minimo <= idadeAnos <= maximo:
                    sub_faixa.append(chave)

        elif 25 <= idadeAnos<= 59:
            id_site = "adulto"
        else:
            id_site = "idoso"



        # --- Chamada do Scraping ---
        dados_vacinas = scrap(id_site,sub_faixa)
        mensagem_final = formatar_mensagem_bot(dados_vacinas)

        faixa_amigavel=dados_vacinas[0]['grupo'] # retorna o nome do grupo através do primeiro elemento no dicionário

        bot.send_message(msg.chat.id,
                         f"✅ Grupo: {faixa_amigavel} ({idadeAnos if idadeAnos >= 1 else idadeMes} {plural('ano','anos',idadeAnos) if idadeAnos>=1 else plural('mês','meses',idadeMes)}).\n⌛ Buscando informações oficiais...")

        # Enviar com parse_mode para aceitar o negrito/itálico do Markdown
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")

    except ValueError:
        bot.reply_to(msg, "Formato inválido! Use DD/MM/AAAA.")

@bot.message_handler(func=lambda msg: msg.text=="Grupo")
def opcoes_grupo(msg):
    markup=types.ReplyKeyboardMarkup(row_width=1,resize_keyboard=True)
    markup.add("Crianca","Adolescente","Adulto","Idoso","Gestante")
    sent_msg=bot.send_message(msg.chat.id,'Informe o grupo para pesquisa.',reply_markup=markup)
    bot.register_next_step_handler(sent_msg,fornece_grupo)


def fornece_grupo(msg):
    id_site=msg.text.lower()
    dados_vacinais = scrap(id_site)
    mensagem_final = formatar_mensagem_bot(dados_vacinais)
    try :

        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown",reply_markup=types.ReplyKeyboardRemove())


    except ValueError:
        bot.reply_to(msg,'Não encontramos dados para esse grupo.')


app = Flask('')
@app.route('/')
def home():
    return "Bot Gotinha está online ! ✅"
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0',port=port)

if __name__ == "__main__":
    t = threading.Thread(target=run)
    t.start()
    print("Bot iniciando...")
    bot.infinity_polling()

