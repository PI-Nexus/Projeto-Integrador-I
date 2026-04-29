from playwright.sync_api import sync_playwright
import time

def buscar_ubs_cnes(municipio, uf):
    #Realiza o scraping no portal CNES para encontrar UBS de uma cidade.
    with sync_playwright() as p:
        # Lançamos o navegador (headless=True para não abrir janela no servidor)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 ...")
        page = context.new_page()

        try:
            # 1. Acessa a página de consulta
            page.goto("https://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp", timeout=60000)
            
            # 2. Seleciona o Estado (UF)
            # O site do CNES usa seletores baseados em ID ou CSS
            page.select_option("select[ng-model='coordenador.estado']", label=uf)
            
            # 3. Aguarda o Município carregar (o site faz uma requisição interna)
            page.wait_for_load_state("networkidle")
            time.sleep(1) # Delay de segurança para o site processar
            
            # 4. Seleciona o Município
            page.select_option("select[ng-model='coordenador.municipio']", label=municipio)
            
            # 5. Filtra por 'CENTRO DE SAUDE/UNIDADE BASICA'
            page.select_option("select[ng-model='coordenador.tipoEstabelecimento']", label="CENTRO DE SAUDE/UNIDADE BASICA")
            
            # 6. Clica no botão Pesquisar (usando o ícone ou classe)
            page.click("button[title='Pesquisar']")
            
            # 7. Espera a tabela de resultados aparecer
            page.wait_for_selector("table tbody tr", timeout=10000)
            
            # 8. Extração dos dados
            rows = page.query_selector_all("table tbody tr")
            ubs_encontradas = []
            
            for row in rows[:3]:  # Pegamos as 3 primeiras para ser rápido
                cols = row.query_selector_all("td")
                if len(cols) >= 3:
                    nome = cols[0].inner_text().strip()
                    endereco = cols[2].inner_text().strip() # Coluna de endereço
                    ubs_encontradas.append({"nome": nome, "endereco": endereco})
            
            browser.close()
            return ubs_encontradas

        except Exception as e:
            print(f"Erro no scraping: {e}")
            browser.close()
            return []