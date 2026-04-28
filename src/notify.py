import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time

# --- CONFIGURAÇÃO DE CAMINHOS ROBUSTA ---
BASE_DIR = Path(__file__).resolve().parent.parent
CALENDARIO_JSON = BASE_DIR / "downloads" / "calendario_completo.json"
AGENDAMENTOS_JSON = BASE_DIR / "data" / "agendamentos.json"

# Garante que a pasta 'data' exista para não dar erro ao salvar
AGENDAMENTOS_JSON.parent.mkdir(parents=True, exist_ok=True)

def carregar_json(caminho):
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_agendamentos(dados):
    # Função interna que grava a lista no arquivo
    with open(AGENDAMENTOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def salvar_agendamento(chat_id, email, vacina_nome, data_alvo):
    """
    ESTA É A FUNÇÃO QUE A MAIN CHAMA.
    Ela recebe os dados soltos, organiza e manda salvar.
    """
    agendamentos = carregar_json(AGENDAMENTOS_JSON)
    
    novo_registro = {
        "chat_id": chat_id,
        "email": email,
        "vacina": vacina_nome,
        "data_alvo": data_alvo.strftime("%Y-%m-%d"),
        "alertas_enviados": []
    }
    
    agendamentos.append(novo_registro)
    salvar_agendamentos(agendamentos)

def calcular_data_alvo(data_nasc_ou_hoje, periodo_texto):
    hoje = datetime.now()
    
    # Extrai números do texto
    numeros = [int(s) for s in periodo_texto.split() if s.isdigit()]
    valor = numeros[0] if numeros else 0

    if "mês" in periodo_texto.lower() or "meses" in periodo_texto.lower():
        return hoje + timedelta(days=valor * 30)
    
    if "ano" in periodo_texto.lower():
        # Se a idade da vacina já passou ou é a idade atual, agenda para 30 dias
        data_aniversario_vacina = data_nasc_ou_hoje + timedelta(days=valor * 365.25)
        
        if data_aniversario_vacina <= hoje:
            return hoje + timedelta(days=30) 
        
        return data_aniversario_vacina

    return hoje + timedelta(days=30)

def loop_notificacao(bot):
    while True:
        try:
            agendamentos = carregar_json(AGENDAMENTOS_JSON)
            agora = datetime.now()
            alterado = False

            for agend in agendamentos:
                data_vencimento = datetime.strptime(agend['data_alvo'], "%Y-%m-%d").date()
                hoje = datetime.now().date() 
                
                dias_restantes = (data_vencimento - hoje).days

                prazos = {10: "alerta_10_dias", 1: "alerta_1_dia", 0: "alerta_hoje"}
                
                if dias_restantes in prazos:
                    label = prazos[dias_restantes]
                    if label not in agend['alertas_enviados']:
                        msg = f"💉 *Lembrete Gotinha*\n\nSua vacina *{agend['vacina']}* está chegando!\n📅 Data: {agend['data_alvo']}"
                        bot.send_message(agend['chat_id'], msg, parse_mode="Markdown")
                        agend['alertas_enviados'].append(label)
                        alterado = True

            if alterado:
                salvar_agendamentos(agendamentos)
        except Exception as e:
            print(f"Erro no loop: {e}")
        
        time.sleep(10)