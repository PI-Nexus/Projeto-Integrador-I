import csv
import os
import smtplib
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
import src.auxiliares

# Caminho seguindo o seu padrão da pasta data/
DATA_DIR = 'data'
CSV_PATH = os.path.join(DATA_DIR, 'agendamentos.csv')

def garantir_diretorio():
    """Garante que a pasta data exista, igual ao seu save_as_file."""
    os.makedirs(DATA_DIR, exist_ok=True)

def salvar_agendamento(chat_id, email, vacina, data_vacinacao):
    """Salva o agendamento no CSV dentro da pasta data/."""
    garantir_diretorio()
    # Abre em modo 'a' (append) para adicionar linhas sem apagar as anteriores
    with open(CSV_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id, email, vacina, data_vacinacao])

def enviar_email(destinatario, vacina, data):
    """Dispara o e-mail de alerta."""
    user = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')

    msg = EmailMessage()
    msg.set_content(f"Olá! O Assistente Gotinha passando para avisar que sua vacina ({vacina}) está próxima: {data}.")
    msg['Subject'] = "Lembrete de Vacinação 💉"
    msg['From'] = user
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def verificar_agendamentos(bot):
    """Varre o arquivo e notifica quem está no período de 3 meses."""
    if not os.path.exists(CSV_PATH):
        return

    hoje = datetime.now()
    prazo_limite = hoje + timedelta(days=90)
    agendamentos_restantes = []

    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for linha in reader:
                if not linha: continue
                chat_id, email, vacina, data_str = linha
                
                # Converte a string do CSV para objeto date para comparar
                data_vacina = datetime.strptime(data_str, '%Y-%m-%d')

                # Verifica se a vacina ocorre nos próximos 3 meses (e não passou)
                if hoje <= data_vacina <= prazo_limite:
                    enviar_email(email, vacina, data_str)
                    try:
                        bot.send_message(chat_id, f"💉 *Lembrete Gotinha!*\nSua vacina *{vacina}* está prevista para {data_str}. Verifique seu e-mail!")
                    except: pass 
                else:
                    # Se ainda falta muito tempo ou já passou, mantém na lista
                    agendamentos_restantes.append(linha)

        # Atualiza o arquivo removendo quem já foi notificado
        with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(agendamentos_restantes)
    except Exception as e:
        print(f"Erro ao processar notificações: {e}")

def sugerir_vacinas(data_vacinas, idade_usuario=None):
    # Se o usuário NÃO informou idade (fluxo por grupo), retorna tudo
    if idade_usuario is None:
        return data_vacinas 
    
    disponiveis = []
    for v in data_vacinas:
        inicio, fim = src.auxiliares.obter_faixa_etaria(v['periodo'])
        
        # LÓGICA: Se a idade do usuário é menor ou igual ao FIM do período,
        # ele ainda pode ou deve tomar a vacina.
        if idade_usuario <= fim:
            disponiveis.append(v)
            
    return disponiveis

def loop_notificacao(bot):
    """Loop diário para a thread de background."""
    while True:
        verificar_agendamentos(bot)
        # Espera 24 horas para a próxima checagem
        time.sleep(10)