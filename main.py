import threading
from flask import Flask
import os
import telebot
import requests
from telebot import types # Import necessário para os botões
from bs4 import BeautifulSoup
from datetime import datetime
import re
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN)

# --- FUNÇÃO DE SCRAPING (MANTIDA) ---
def scrap(grupo_id):
    url = 'https://www.gov.br/saude/pt-br/vacinacao/calendario'
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.find('div', id=grupo_id)
        
        if not container:
            return []

        lista_vacinas = []
        nome_grupo = container.find('span', class_='titulo').get_text(strip=True)
        blocos_periodo = container.select('ul.servicos > li')

        for bloco in blocos_periodo:
            tag_periodo = bloco.find('a', class_='primeiro-nivel')
            if not tag_periodo: continue
            nome_periodo = tag_periodo.get_text(strip=True)

            vacinas_html = bloco.select('ul.servicos-segundo-nivel .menu')
            for item in vacinas_html:
                titulo_tag = item.find('p', class_='vacina__titulo')
                if titulo_tag:
                    dose_interna = titulo_tag.find('span', class_='vacina__dose')
                    dose_texto = dose_interna.extract().get_text(strip=True) if dose_interna else "Dose única/Reforço"
                    nome_vacina = titulo_tag.get_text(strip=True)
                    
                    lista_vacinas.append({
                        "grupo": nome_grupo,
                        "periodo": nome_periodo,
                        "vacina": nome_vacina,
                        "dose" : dose_texto
                    })
        return lista_vacinas
    except Exception as e:
        print(f"Erro no scraping: {e}")
        return None

# --- FORMATAÇÃO (MANTIDA) ---
def formatar_mensagem_bot(dados_json):
    if dados_json is None:
        return "❌ Erro ao acessar o site do Ministério da Saúde."
    if not dados_json:
        return "⚠️ Nenhuma informação encontrada para esta categoria."

    texto = f"💉 *CALENDÁRIO: {dados_json[0]['grupo'].upper()}*\n"
    texto += "________________________________\n\n"

    periodo_atual = ""
    for item in dados_json:
        if item['periodo'] != periodo_atual:
            periodo_atual = item['periodo']
            texto += f"\n📍 *{periodo_atual}*\n"
        texto += f"  • {item['vacina']} _{item['dose']}_\n"

    return texto

# --- HANDLERS ---

@bot.message_handler(commands=['start', 'help'])
def start(msg: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Início', 'Vacinas', 'Help')
    bot.send_message(msg.chat.id, 'Olá, sou o seu assistente virtual! Selecione uma opção abaixo.', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg, "Você está no início do assistente virtual! Estou aqui para te ajudar a encontrar as vacinas disponíveis para você. Selecione 'Vacinas' para começar.")

@bot.message_handler(func=lambda msg: msg.text == "Vacinas")
def pedir_data_nascimento(msg):
    sent_msg = bot.reply_to(msg, "Para consultar as vacinas disponíveis, informe a data de nascimento da pessoa no formato DD/MM/AAAA.")
    bot.register_next_step_handler(sent_msg, processar_data)

def processar_data(msg):
    data_texto = msg.text
    try:
        data_nascimento = datetime.strptime(data_texto, "%d/%m/%Y")
        hoje = datetime.now()
        idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

        if idade < 0:
            bot.reply_to(msg, "A data está inválida! Por favor, selecione uma data real!'.")
            return

        # --- Mapeamento para o Scraping ---
        if idade <= 10:
            id_site = "crianca"
            faixa_amigavel = "Criança"
        elif 11 <= idade <= 19:
            id_site = "adolescente"
            faixa_amigavel = "Adolescente"
        elif 20 <= idade <= 59:
            id_site = "adulto"
            faixa_amigavel = "Adulto"
        else:
            id_site = "idoso"
            faixa_amigavel = "Idoso"

        bot.send_message(msg.chat.id, f"✅ Grupo: {faixa_amigavel} ({idade} anos).\n⌛ Buscando informações oficiais...")

        # --- Chamada do Scraping ---
        dados_vacinas = scrap(id_site)
        mensagem_final = formatar_mensagem_bot(dados_vacinas)
        
        # Enviar com parse_mode para aceitar o negrito/itálico do Markdown
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")
                                  
    except ValueError:
        bot.reply_to(msg, "Formato inválido! Use DD/MM/AAAA.")

@bot.message_handler(func=lambda msg: msg.text == "Help")
def resposta_help(msg):
    bot.reply_to(msg, "Para obter ajuda, acesse: \nhttps://LinkDoSite.")
    #Obs: fazer um site simples em html/css/js para melhorar a experiencia do usuário e suprir dúvidas


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