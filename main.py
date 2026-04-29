# Bibliotecas padrão
import os
import threading
from datetime import datetime

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
from src.buscar_postos import buscar_postos_proximos,threading_search,start_drivers
import src.notify as notify
from src.auxiliares import gerar_botoes_vacinas, calcular_data_alvo, definir_categoria_por_idade, converter_periodo_para_meses


# 1. Configurações Iniciais
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN)

user_states = {}

# 2. Definição do Servidor Flask (Precisa estar aqui no escopo global)
app = Flask('')

@app.route('/')
def home():
    return "Bot Gotinha está online ! ✅"

# HANDLERS DE INTERFACE

@bot.message_handler(commands=['start', 'help'])
def comandos(msg):
    # baixa dados de cobertura vacinal 
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

@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg, "Você está no início! Selecione 'Vacinas' ou consulte as UBS próximas pelo GPS.")

# FLUXO DE COBERTURA VACINAL — PONTO DE ENTRADA
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
    bot.send_message(
        msg.chat.id,
        "Como deseja consultar a cobertura vacinal?",
        reply_markup=markup,
    )

# Fornece regiões para seleção do usuário
def escolher_regiao(msg):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for regiao in regioes.keys():
        markup.add(regiao)
    markup.add( "Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, "Escolha uma região:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Realizar nova consulta")
def nova_consulta(msg):
    menu_cobertura(msg)
    
#Conexão Dashboard
@bot.message_handler(func=lambda msg: msg.text == "Dashboard Cobertura Vacinal")
def dashboard(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Voltar ao Menu Principal')
    link = "https://app.powerbi.com/view?r=eyJrIjoiMjFmM2ViMWQtZGI0OS00NjJkLTkxYmQtMGI5MmYzYjliOWUzIiwidCI6ImNmNzJlMmJkLTdhMmItNDc4My1iZGViLTM5ZDU3YjA3Zjc2ZiIsImMiOjR9"
    bot.send_message(msg.chat.id, f"<a href = '{link}'> Dashboard Cobertura Vacinal </a>", reply_markup=markup, parse_mode="HTML")

#teste

# OPÇÃO 1 — POR ESTADO (fluxo original, apenas entry-point novo)
@bot.message_handler(func=lambda msg: msg.text == "Estado")
def cobertura_por_estado(msg):
    # Limpa modo para garantir fluxo de estado
    user_states[msg.chat.id] = {"modo_cobertura": "estado"}
    escolher_regiao(msg)

# OPÇÃO 2 — POR MUNICÍPIO
@bot.message_handler(func=lambda msg: msg.text == "Município")
def cobertura_por_municipio_inicio(msg):
    # Guarda no estado do usuário que o próximo fluxo de região/estado
    # será para município
    user_states[msg.chat.id] = {"modo_cobertura": "municipio"}
    escolher_regiao_municipio(msg)

def escolher_regiao_municipio(msg):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for regiao in regioes.keys():
        markup.add(regiao)
    markup.add("Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, "Escolha a região do município:", reply_markup=markup)

# Handler de regiões para fluxo de município
# Necessário distinguir se o usuário está no fluxo "estado" ou "município".
# A forma mais limpa: usar o campo user_states[chat_id]["modo_cobertura"].
@bot.message_handler(func=lambda msg: msg.text in regioes.keys())
def mostrar_estados_dispatch(msg):
    """Redireciona para o fluxo correto conforme o modo escolhido."""
    estado_usuario = user_states.get(msg.chat.id, {})
    modo = estado_usuario.get("modo_cobertura", "estado")

    estados_da_regiao = regioes[msg.text]
    markup = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
    for estado in estados_da_regiao:
        markup.add(estado)
    markup.add("Voltar")

    # Salva a lista de estados da região para saber quais são válidos no próximo passo
    if msg.chat.id not in user_states:
        user_states[msg.chat.id] = {}
    user_states[msg.chat.id]["regiao_atual"] = msg.text

    bot.send_message(msg.chat.id, "Escolha o estado:", reply_markup=markup)

# Define consulta por estado ou município com base no modo
@bot.message_handler(func=lambda msg: msg.text in sum(regioes.values(), []))
def estado_selecionado_dispatch(msg):
    """Direciona para consulta por estado ou para pedir o município."""
    estado_usuario = user_states.get(msg.chat.id, {})
    modo = estado_usuario.get("modo_cobertura", "estado")

    if modo == "municipio":
        # Salva o estado e pede o município
        user_states[msg.chat.id]["uf_selecionada"] = msg.text
        bot.send_message(
            msg.chat.id,
            f"Estado selecionado: <b>{msg.text}</b>\n\nDigite o nome do município:",
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        bot.register_next_step_handler(msg, processar_municipio)
    else:
        # Fluxo original de estado
        processar_estado(msg)

def processar_municipio(msg):
    municipio = msg.text.strip()
    estado = user_states.get(msg.chat.id, {}).get("uf_selecionada", "")

    if not estado:
        bot.send_message(msg.chat.id, "⚠️ Erro interno: estado não encontrado. Tente novamente.")
        menu_cobertura(msg)
        return

    bot.send_message(msg.chat.id, "🔎 Buscando dados... aguarde ⏳")

    resposta = buscar_cobertura_municipio(estado, municipio)

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Realizar nova consulta", "Voltar ao Menu Principal")

    # Reseta o modo para não interferir em próximas consultas
    user_states.pop(msg.chat.id, None)

    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")


# OPÇÃO 3 — RANKING DE ESTADOS
@bot.message_handler(func=lambda msg: msg.text == "Ranking de Estados 🇧🇷")
def cobertura_ranking(msg):
    bot.send_message(msg.chat.id, "🔎 Calculando ranking nacional... aguarde ⏳")

    resposta = calcular_media_estados()

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Realizar nova consulta", "Voltar ao Menu Principal")

    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "Voltar")
def voltar_para_regioes(msg):
    # Preserva modo_cobertura caso exista, retorna para a tela de regiões
    modo = user_states.get(msg.chat.id, {}).get("modo_cobertura", "estado")
    if modo == "municipio":
        escolher_regiao_municipio(msg)
    else:
        escolher_regiao(msg)

def processar_estado(msg):
    estado = msg.text.strip().upper()

    bot.send_message(msg.chat.id, "🔎 Buscando dados atualizados... aguarde um instante ⏳")

    resposta = buscar_cobertura_estado(estado)

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Realizar nova consulta", "Voltar ao Menu Principal")

    # Limpa o modo para não interferir em próximas consultas
    user_states.pop(msg.chat.id, None)

    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

    
# FLUXO DE LOCALIZAÇÃO
@bot.message_handler(func=lambda msg: msg.text == "Unidades próximas")
def pedir_localizacao(msg):
    start_drivers()
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_gps = types.KeyboardButton("📍 Compartilhar minha localização atual", request_location=True)
    markup.add(btn_gps, "Voltar ao Menu Principal")
    
    bot.send_message(msg.chat.id, 
        "Clique no botão abaixo para encontrar as UBS mais próximas.",
        reply_markup=markup)


@bot.message_handler(content_types=['location'])
def tratar_localizacao(msg):

    bot.send_message(msg.chat.id,"🔎 Buscando UBS próximas… aguarde um instante.",parse_mode="Markdown")
    try:
        lat = msg.location.latitude
        lon = msg.location.longitude
        postos_proximos = buscar_postos_proximos(lat, lon)
        links= threading_search(postos_proximos)

        # Retorno das coordenadas em formato de lista/texto monoespaçado
        message = ''
        for posto in postos_proximos:
            link=links[posto['nome']]
            message += f'\n<a href="{link}">{posto["nome"]}</a>\n'

        bot.send_message(msg.chat.id, message, parse_mode="HTML")


    except Exception as e:
        print(f"Erro GPS: {e}")
        bot.send_message(msg.chat.id, "⚠️ Erro ao consultar o portal de saúde.")

# FLUXO DE VACINAS
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
    try:
        data_nascimento = datetime.strptime(msg.text, "%d/%m/%Y")
        hoje = datetime.now()
        idade_anos = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

        id_site = definir_categoria_por_idade(idade_anos)
        dados_vacinas = scrap(id_site) 

        if not dados_vacinas:
            bot.send_message(msg.chat.id, f"✅ Não encontrei vacinas pendentes para sua faixa ({id_site}).")
            servicos(msg)
            return

        # Filtro para crianças
        if idade_anos < 12:
            idade_meses_total = (idade_anos * 12) + (hoje.month - data_nascimento.month)
            vacinas_exibicao = [
                v for v in dados_vacinas 
                if converter_periodo_para_meses(v['periodo']) >= idade_meses_total
            ]
        else:
            vacinas_exibicao = dados_vacinas

        user_states[msg.chat.id] = {
            'data_nasc': data_nascimento,
            'vacinas': vacinas_exibicao,
            'indice_atual': 0
        }

        # Chamada dos botões
        exibir_vacina_atual(msg.chat.id, 0)

    except Exception as e:
        bot.reply_to(msg, "⚠️ Erro ao processar. Certifique-se de usar DD/MM/AAAA.")

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
        user_states[msg.chat.id] = {
            'data_nasc': datetime.now(),
            'vacinas': dados_vacinais,
            'indice_atual': 0
        }
        exibir_vacina_atual(msg.chat.id, 0)
    except Exception:
        bot.reply_to(msg, 'Não encontramos dados.')

def exibir_vacina_atual(chat_id, indice):
    dados = user_states.get(chat_id)
    if not dados or not dados['vacinas']:
        bot.send_message(chat_id, "Nenhuma vacina pendente encontrada.")
        return

    vacinas = dados['vacinas']
    
    if indice >= len(vacinas):
        bot.send_message(chat_id, "✅ Você já visualizou todas as opções disponíveis!")
        servico_final_manual(chat_id)
        return

    user_states[chat_id]['indice_atual'] = indice
    v = vacinas[indice]

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_agendar = types.InlineKeyboardButton("🔔 Agendar esta", callback_data="agendar_esta")
    btn_proxima = types.InlineKeyboardButton("⏭️ Já tomei / Próxima", callback_data="proxima_vacina")
    markup.add(btn_agendar, btn_proxima)

    texto = (f"📍 *Opção {indice + 1} de {len(vacinas)}*\n\n"
             f"💉 *Vacina:* {v['vacina']}\n"
             f"📅 *Recomendação:* {v['periodo']}\n\n"
             "Deseja agendar um lembrete ou ver a próxima?")
    
    bot.send_message(chat_id, texto, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "proxima_vacina":
        novo_indice = user_states[chat_id].get('indice_atual', 0) + 1
        bot.delete_message(chat_id, call.message.message_id)
        exibir_vacina_atual(chat_id, novo_indice)

    elif call.data == "agendar_esta":
        indice = user_states[chat_id]['indice_atual']
        vacina = user_states[chat_id]['vacinas'][indice]
        
        bot.answer_callback_query(call.id, "Iniciando agendamento...")
        bot.send_message(chat_id, f"💉 Selecionada: *{vacina['vacina']}*\n\nInforme seu e-mail para receber os alertas:", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, finalizar_agendamento, vacina['vacina'], vacina['periodo'])

def finalizar_agendamento(msg, vacina_nome, periodo):
    chat_id = msg.chat.id
    # Proteção caso o estado tenha sido perdido
    data_nasc = user_states.get(chat_id, {}).get('data_nasc', datetime.now())
    
    data_alvo = notify.calcular_data_alvo(data_nasc, periodo)
    notify.salvar_agendamento(chat_id, msg.text, vacina_nome, data_alvo)
    
    bot.send_message(chat_id, f"✅ Agendado com sucesso para {data_alvo.strftime('%d/%m/%Y')}!")
    servico_final(msg)

def servico_final_manual(chat_id):
    """Versão da servico_final que aceita chat_id direto"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Encerrar', 'Continuar')
    bot.send_message(chat_id, 'Deseja realizar outra consulta?', reply_markup=markup)

# FAQ E ENCERRAMENTO
@bot.message_handler(func=lambda msg: msg.text == "FAQ")
def faq_menu(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Documentos necessários', 'Reações comuns', 'Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "📌 *Dúvidas Frequentes*", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "Documentos Necessários")
def faq_documents(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, "Documento com Foto e Caderneta de Vacinação",
    reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "Reações Comuns")
def faq_reactions(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Voltar ao Menu Principal')
    bot.send_message(msg.chat.id, """Febre Leve e Cansaço\n
    Duração de 1 até 3 dias""", reply_markup=markup, parse_mode="Markdown")

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
    markup.add('Notificar Próxima Vacina','Encerrar', 'Continuar')
    bot.send_message(msg.chat.id, 'Deseja realizar outra consulta?', reply_markup=markup)
# EXECUÇÃO

if __name__ == "__main__":
    bot.remove_webhook()
    
    port = int(os.environ.get("PORT", 8080))
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False))
    t.daemon = True
    t.start()

    threading.Thread(target=notify.loop_notificacao, args=(bot,), daemon=True).start()
    
    print("Bot Gotinha Ativado com Localização! 🚀")
    bot.infinity_polling()