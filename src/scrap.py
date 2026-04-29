import os
from bs4 import BeautifulSoup
import requests


def save_as_file():
    """
      Realiza o download da página de calendário de vacinação do Ministério da Saúde
      e salva o conteúdo HTML localmente.

      A função cria o diretório 'data' caso não exista e salva o conteúdo
      em 'data/scrap.txt'.
    """
    os.makedirs('data',exist_ok=True)
    url = 'https://www.gov.br/saude/pt-br/vacinacao/calendario'
    response = requests.get(url, timeout=10)
    with open('data/scrap.txt','w',encoding='utf-8') as my_file:
        my_file.write(str(response.text))



# FUNÇÃO DE SCRAPING

"""
grupo_id: ID do grupo no HTML (ex: crianças, adolescentes, etc.)
periodo: Lista opcional de períodos a serem filtrados
"""
def scrap(grupo_id,periodo:list | None = None):
    #Realiza o scraping do calendário de vacinação a partir do HTML salvo localmente.
    try:
        save_as_file()
        with open('data/scrap.txt', 'r', encoding='utf-8') as scrap_file:
            container = scrap_file.read()
            if not container:
                save_as_file()
                container = scrap_file.read()

        if not container:
            return []

        soup = BeautifulSoup(container, 'html.parser')
        container = soup.find('div', id=grupo_id)

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
                    if periodo is None or not periodo:
                        lista_vacinas.append({
                            "grupo": nome_grupo,
                            "periodo": nome_periodo,
                            "vacina": nome_vacina,
                            "dose": dose_texto
                        })
                    else :
                        if nome_periodo in periodo:
                            lista_vacinas.append({
                                "grupo": nome_grupo,
                                "periodo": nome_periodo,
                                "vacina": nome_vacina,
                                "dose": dose_texto
                            })


        return lista_vacinas
    except Exception as e:
        print(f"Erro no scraping: {e}")
        return None


# FORMATAÇÃO
def formatar_mensagem_bot(dados_json):
    if dados_json is None:
        return "❌ Erro ao acessar o site do Ministério da Saúde."
    if not dados_json:
        return "⚠️ Nenhuma informação encontrada para esta categoria."

    texto = f"💉 *CALENDÁRIO: {dados_json[0]['grupo'].upper()}*\n"
    texto += "________________________________\n"

    periodo_atual = ""
    for item in dados_json:
        if item['periodo'] != periodo_atual:
            periodo_atual = item['periodo']
            texto += f"\n📍 *{periodo_atual}*\n"
        texto += f"  • {item['vacina']} _{item['dose']}_\n"


    return texto

