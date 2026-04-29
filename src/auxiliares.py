import re 
from telebot import types
from dateutil.relativedelta import relativedelta


def plural(palavra_singular, palavra_plural, quantidade):
    return palavra_singular if quantidade == 1 else palavra_plural

def extrair_idades(periodo_str):
    # Extrai todos os números (ex: "9 a 14" -> [9, 14])
    numeros = [int(n) for n in re.findall(r'\d+', periodo_str)]
    return numeros[0], numeros[1] if len(numeros) > 1 else numeros[0]

def obter_faixa_etaria(periodo_str):
    # Extrai todos os números. Ex: "9 a 14 anos" -> [9, 14]
    numeros = [int(n) for n in re.findall(r'\d+', periodo_str)]
    
    if len(numeros) == 1:
        return numeros[0], numeros[0] # Ex: "10 anos" (fixo)
    elif len(numeros) >= 2:
        return numeros[0], numeros[1] # Ex: 9 e 14
    return 0, 99 # Fallback

def gerar_botoes_vacinas(lista_vacinas):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for v in lista_vacinas:
        markup.add(v['vacina'])
    return markup


def calcular_data_alvo(data_nascimento, periodo_str):
    # Se for "Ao nascer", a data é a própria data de nascimento
    if "nascer" in periodo_str.lower():
        return data_nascimento
    
    # Busca números na string (ex: "2" de "2 meses" ou "9" de "9 a 14 anos")
    match = re.search(r'\d+', periodo_str)
    if not match:
        return None
    
    valor = int(match.group())
    
    if "mes" in periodo_str.lower():
        return data_nascimento + relativedelta(months=valor)
    elif "ano" in periodo_str.lower():
        return data_nascimento + relativedelta(years=valor)
    
    return None