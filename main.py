
import telebot
import requests
from telebot import types # Import necessário para os botões
from bs4 import BeautifulSoup
from datetime import datetime
import re
TOKEN = "INSERIR_TOKEN_AQUI" 

bot = telebot.TeleBot(TOKEN)

# --- FUNÇÃO DE SCRAPING (CORRIGIDA) ---
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
                    if dose_interna:
                        dose_texto = dose_interna.extract().get_text(strip=True)
                    else:
                        dose_texto = "Dose única/Reforço"
                    
                    nome_vacina = titulo_tag.get_text(strip=True)
                    # Criando o objeto JSON (Dicionário)
                    lista_vacinas.append({
                        "grupo": nome_grupo,
                        "periodo": nome_periodo,
                        "vacina": nome_vacina,
                        "dose" : dose_texto
                        #"dose": dose_tag.get_text(strip=True) if dose_tag else "Dose única/Reforço"
                    })
        return lista_vacinas
    except Exception as e:
        print(f"Erro no scraping: {e}")
        return None
    
def formatar_mensagem_bot(dados_json):
    if dados_json is None:
        return "❌ Erro ao acessar o site do Ministério da Saúde."
    if not dados_json:
        return "⚠️ Nenhuma informação encontrada para esta categoria."

    # Cabeçalho usando o primeiro item para pegar o nome do grupo
    texto = f"💉 *CALENDÁRIO: {dados_json[0]['grupo'].upper()}*\n"
    texto += "________________________________\n\n"

    periodo_atual = ""
    for item in dados_json:
        # Se mudou o período (ex: de 'Ao nascer' para '2 meses'), adiciona o subtítulo
        if item['periodo'] != periodo_atual:
            periodo_atual = item['periodo']
            texto += f"\n📍 *{periodo_atual}*\n"
        
        # Adiciona a vacina e a dose
        texto += f"  • {item['vacina']} _{item['dose']}_\n"

    return texto

# --- HANDLERS DO BOT ---

@bot.message_handler(commands=['start', 'help'])
def start(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Início', 'Vacinas', 'Help')
    bot.send_message(msg.chat.id, 'Olá, sou o bot Gotinha! Clique no botão abaixo para começar.', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Vacinas")
def pedir_idade(msg):
    # Opção Calendário Completo ou Calendário Até Hoje
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Calendário Completo', 'Calendário Até Hoje')
    bot.send_message(msg.chat.id, "Você deseja ver o calendário completo do seu grupo ou apenas o que já deveria ter tomado até hoje?", reply_markup=markup)
    bot.register_next_step_handler(msg, processar_opcao)

    #sent_msg = bot.reply_to(msg, "Digite a data de nascimento formatada: [dd/mm/aaaa]")
    #bot.register_next_step_handler(sent_msg, processar_idade)

def processar_opcao(msg):
    opcao = msg.text
    
    # Se o usuário clicar em "Início" ou "Help" no meio do processo, nós paramos o fluxo de vacinas
    if opcao in ['Início', 'Help']:
        if opcao == 'Início': resposta_inicio(msg)
        else: resposta_help(msg)
        return

    if opcao not in ['Calendário Completo', 'Calendário Até Hoje']:
        bot.reply_to(msg, "⚠️ Por favor, use apenas os botões do menu.")
        # Em vez de chamar pedir_idade, enviamos apenas a instrução de novo
        return pedir_idade(msg)

    sent_msg = bot.send_message(
        msg.chat.id, 
        f"✅ {opcao} selecionado.\n\nDigite a data de nascimento [dd/mm/aaaa]:", 
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(sent_msg, processar_idade, opcao)

def processar_idade(msg, opcao):
    # Se o usuário desistir e clicar em um comando de barra (ex: /start)
    if msg.text.startswith('/'):
        bot.clear_step_handler_by_chat_id(chat_id=msg.chat.id)
        return start(msg)

    data_texto = msg.text
    try:
        hoje = datetime.now()
        data_nasc = datetime.strptime(data_texto, "%d/%m/%Y")
        
        # Lógica de idade...
        idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
        idade_meses = (hoje.year - data_nasc.year) * 12 + (hoje.month - data_nasc.month)
        if hoje.day < data_nasc.day: idade_meses -= 1
        
    except ValueError:
        sent_msg = bot.reply_to(msg, "❌ Data inválida! Use o formato dia/mês/ano (ex: 20/05/2010):")
        return bot.register_next_step_handler(sent_msg, processar_idade, opcao)

    # Segue para o scraping...
    if idade <= 10: id_site = "crianca"
    elif 11 <= idade <= 19: id_site = "adolescente"
    elif 20 <= idade <= 59: id_site = "adulto"
    else: id_site = "idoso"

    bot.send_message(msg.chat.id, "🔎 Consultando banco de dados oficial... ⏳")
    
    dados_json = scrap(id_site)
    if opcao == "Calendário Até Hoje":
        dados_json = filtrar_por_idade(dados_json, idade_meses, idade, id_site)
    
    resultado = formatar_mensagem_bot(dados_json)
    bot.send_message(msg.chat.id, resultado, parse_mode="Markdown")
    
    # Restaura o menu principal
    markup_menu = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup_menu.add('Início', 'Vacinas', 'Help')
    bot.send_message(msg.chat.id, "O que deseja fazer agora?", reply_markup=markup_menu)

def filtrar_por_idade(dados, meses_usuario, anos_usuario, id_site):
    dados_filtrados = []
    
    for item in dados:
        periodo = item['periodo'].lower()
        
        # 1. Busca todos os números no texto (ex: "9 a 14" vira [9, 14])
        numeros = re.findall(r'\d+', periodo)
        valores = [int(n) for n in numeros]
        
        # Se for criança e o período menciona "meses"
        if "mes" in periodo and id_site == "crianca":
            if not valores or meses_usuario >= valores[0]:
                dados_filtrados.append(item)
            continue

        # Se houver um intervalo (ex: "9 a 14 anos")
        if len(valores) >= 2 and "ano" in periodo:
            minimo, maximo = valores[0], valores[1]
            if minimo <= anos_usuario <= maximo:
                dados_filtrados.append(item)
        
        # Se houver apenas um número (ex: "15 anos" ou "aos 10 anos")
        elif len(valores) == 1 and "ano" in periodo:
            if anos_usuario >= valores[0]:
                dados_filtrados.append(item)
        
        # Casos especiais: "Ao nascer" ou períodos sem números
        elif "nascer" in periodo or not valores:
            dados_filtrados.append(item)
            
    return dados_filtrados

@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg, "Como posso te ajudar?")

@bot.message_handler(func=lambda msg: msg.text == "Help")
def resposta_help(msg):
    bot.reply_to(msg, "Eu ajudo você a consultar o calendário de vacinação oficial. Clique em 'Vacinas' e informe a idade.")

#print(scrap("crianca"))
print("Bot iniciado...")
bot.infinity_polling()
