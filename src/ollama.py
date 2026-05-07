import pandas as pd
import json

def obter_contexto_local():
    # Carrega os postos do seu CSV atual
    df_postos = pd.read_csv('src/Unidade_basica_de_saude.csv', sep=';')
    # Resumo para não ocupar muito espaço no processamento
    postos_texto = df_postos[['NOME', 'LOGRADOURO']].to_string(index=False)
    
    # Carrega o calendário vacinal do seu JSON
    with open('downloads/calendario_completo.json', 'r', encoding='utf-8') as f:
        calendario = json.load(f)
    
    return f"Dados de Postos em SJC:\n{postos_texto}\n\nCalendário Vacinal:\n{calendario}"