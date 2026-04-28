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
from src.scrap_cobertura import (
    buscar_cobertura_estado,
    buscar_cobertura_municipio,
    calcular_media_estados,
    baixar_e_tratar_dados,
)
from src.buscar_postos import buscar_postos_proximos,threading_search,start_drivers

import src.notificador as notificador
from src.auxiliares import gerar_botoes_vacinas, calcular_data_alvo


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

# --- HANDLERS DE INTERFACE ---

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
        "Dashboard Cobertura Vacinal",
        'Unidades próximas', 
        'FAQ'
    )
    bot.send_message(msg.chat.id, 'Olá! Eu sou o Assistente Gotinha. Como posso te ajudar?', reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Início")
def resposta_inicio(msg):
    bot.reply_to(msg, "Você está no início! Selecione 'Vacinas' ou consulte as UBS próximas pelo GPS.")

# --- FLUXO DE COBERTURA VACINAL ---
regioes = {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"]
}

# -------------------------------------------------------
# FLUXO DE COBERTURA VACINAL — PONTO DE ENTRADA
# -------------------------------------------------------

@bot.message_handler(func=lambda msg: msg.text == "Cobertura Vacinal")
def menu_cobertura(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(
        "Por Estado",
        "Por Município",
        "🇧🇷 Ranking de Estados",
        "Voltar ao Menu Principal",
    )
    bot.send_message(
        msg.chat.id,
        "Como deseja consultar a cobertura vacinal?",
        reply_markup=markup,
    )

# Mostra regiões para o usuário escolher
def escolher_regiao(msg):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for regiao in regioes.keys():
        markup.add(regiao)
    markup.add("Digitar estado manualmente", "Voltar ao Menu Principal")
    bot.send_message(msg.chat.id, "Escolha uma região:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Realizar nova consulta")
def nova_consulta(msg):
    menu_cobertura(msg)

@bot.message_handler(func=lambda msg: msg.text == "Digitar estado manualmente")
def pedir_estado_manual(msg):
    user_states[msg.chat.id] = {"modo_cobertura": "estado"}
    bot.send_message(msg.chat.id, "Digite a sigla do estado (ex: SP):")
    bot.register_next_step_handler(msg, processar_estado)

# -------------------------------------------------------
# OPÇÃO 1 — POR ESTADO (fluxo original, apenas entry-point novo)
# -------------------------------------------------------

@bot.message_handler(func=lambda msg: msg.text == "Por Estado")
def cobertura_por_estado(msg):
    # Limpa modo para garantir fluxo de estado
    user_states[msg.chat.id] = {"modo_cobertura": "estado"}
    escolher_regiao(msg)

# -------------------------------------------------------
# OPÇÃO 2 — POR MUNICÍPIO
# -------------------------------------------------------

@bot.message_handler(func=lambda msg: msg.text == "Por Município")
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

# Decide se vai consultar estado ou pedir município conforme o modo
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

    # Limpa o modo para não interferir em próximas consultas
    user_states.pop(msg.chat.id, None)

    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

# -------------------------------------------------------
# OPÇÃO 3 — RANKING DE ESTADOS
# -------------------------------------------------------

@bot.message_handler(func=lambda msg: msg.text == "🇧🇷 Ranking de Estados")
def cobertura_ranking(msg):
    bot.send_message(msg.chat.id, "🔎 Calculando ranking nacional... aguarde ⏳")

    resposta = calcular_media_estados()

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("Realizar nova consulta", "Voltar ao Menu Principal")

    bot.send_message(msg.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.text == "Voltar")
def voltar_para_regioes(msg):
    # Preserva o modo_cobertura se existir, volta só para a tela de regiões
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

    


@bot.message_handler(func=lambda msg: msg.text == "Dashboard Cobertura Vacinal")
def dashboard(msg):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add('Voltar ao Menu Principal')
    link = "https://app.powerbi.com/view?r=eyJrIjoiMjFmM2ViMWQtZGI0OS00NjJkLTkxYmQtMGI5MmYzYjliOWUzIiwidCI6ImNmNzJlMmJkLTdhMmItNDc4My1iZGViLTM5ZDU3YjA3Zjc2ZiIsImMiOjR9"
    bot.send_message(msg.chat.id, f"<a href = '{link}'> Dashboard Cobertura Vacinal </a>", reply_markup=markup, parse_mode="HTML")

# --- FLUXO DE LOCALIZAÇÃO (DESTAQUE DA SPRINT) ---

@bot.message_handler(func=lambda msg: msg.text == "Unidades próximas")
def pedir_localizacao(msg):
    start_drivers()
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_gps = types.KeyboardButton("📍 Compartilhar minha localização atual", request_location=True)
    markup.add(btn_gps, "Voltar ao Menu Principal")
    
    bot.send_message(msg.chat.id, 
        "Para encontrar as UBS mais próximas, clique no botão abaixo para enviar seu GPS.", 
        reply_markup=markup)


@bot.message_handler(content_types=['location'])
def tratar_localizacao(msg):

    bot.send_message(msg.chat.id,"🔎 Buscando UBS próximas… aguarde um instante",parse_mode="Markdown")
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

        user_states[msg.chat.id] = {
            'idade': idadeAnos,
            'vacinas': dados_vacinas
        }

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
        #print(dados_vacinais)
        user_states[msg.chat.id] = {
            'idade': None,
            'vacinas': dados_vacinais
        }
        mensagem_final = formatar_mensagem_bot(dados_vacinais)
        bot.send_message(msg.chat.id, mensagem_final, parse_mode="Markdown")
        # Opção notificação vacina mais próxima
        servico_final(msg)
    except Exception:
        bot.reply_to(msg, 'Não encontramos dados.')

@bot.message_handler(func=lambda msg: msg.text == "Notificar Próxima Vacina")    
def notificar(msg):
    # 1. Recupera os dados (aqui você usaria sua lógica de estado ou banco)
    # idade_user pode ser um int (ex: 10) ou None (se foi por grupo)
    dados = user_states.get(msg.chat.id)
    if not dados:
        bot.send_message(msg.chat.id, "Por favor, informe sua idade ou grupo primeiro.")
        return

    idade_atual = dados['idade']
    vacinas_do_scrap = dados['vacinas']

    # 2. Chama a lógica do notificador
    proximas = notificador.sugerir_vacinas(
        data_vacinas=vacinas_do_scrap, 
        idade_usuario=idade_atual
    )

    if proximas:
        # Se veio do fluxo de IDADE, pegamos a primeira (mais próxima)
        # Se veio do fluxo de GRUPO, 'proximas' contém a lista toda
        if idade_atual is not None:
            proxima = proximas[0]
            texto = (
                f"✅ Com base na sua idade ({idade_atual} anos), a próxima vacina é:\n\n"
                f"💉 *{proxima['vacina']}*\n"
                f"📅 Período: {proxima['periodo']}\n"
                f"ℹ️ Dose: {proxima['dose'].strip()}\n\n"
                "📧 Informe seu e-mail para agendar o lembrete:"
            )
            bot.send_message(msg.chat.id, texto, parse_mode="Markdown")
            # Registra o próximo passo passando os dados da vacina específica
            bot.register_next_step_handler(msg, finalizar_agendamento, proxima['vacina'], proxima['periodo'])
        
        else:
            # Fluxo por GRUPO: O usuário precisa escolher qual vacina da lista
            texto = "📋 Escolha qual dessas vacinas você deseja monitorar (digite o nome ou selecione):"
            # Aqui você poderia gerar botões dinâmicos com a lista de 'proximas'
            markup = gerar_botoes_vacinas(proximas) 
            bot.send_message(msg.chat.id, texto, reply_markup=markup)
            
    else:
        bot.send_message(msg.chat.id, "Não encontrei vacinas pendentes para o seu perfil.")
     
def finalizar_agendamento(msg, vacina_nome, data_proxima):
    email_user = msg.text
    chat_id = msg.chat.id

    dados = user_states.get(chat_id)
    data_nasc = dados.get('data_nasc')
    proxima = calcular_data_alvo(data_nasc, data_proxima)

    if "@" not in email_user:
        bot.send_message(chat_id, "❌ E-mail inválido. Tente clicar no botão novamente.")
        return
    
    notificador.salvar_agendamento(msg.chat.id, email_user, vacina_nome, proxima)
    bot.send_message(msg.chat.id, f"✅ Confirmado! Avisaremos em {email_user} sobre a vacina {vacina_nome}.")
    servicos(msg)

# --- FAQ E ENCERRAMENTO ---

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
# --- EXECUÇÃO ---

if __name__ == "__main__":
    bot.remove_webhook()
    
    # Thread do Flask usando a variável 'app' definida no topo
    port = int(os.environ.get("PORT", 8080))
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False))
    t.daemon = True
    t.start()

    t_notifica = threading.Thread(target=notificador.loop_notificacao, args=(bot,))
    t_notifica.daemon = True
    t_notifica.start()
    
    print("Bot Gotinha Ativado com Localização! 🚀")
    bot.infinity_polling()