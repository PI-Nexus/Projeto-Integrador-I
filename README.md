Manual do Usuário — Bot de Vacinação
1. Visão Geral
O bot de vacinação (@Gotinha_bot) é um assistente Telegram para consulta rápida de calendários vacinais do Ministério da Saúde com base em:

Seleção de grupo (Criança, Adolescente, Adulto, Idoso, Gestante)

Pesquisa por data de nascimento (idade atual)

A base de dados é obtida via scraping de https://www.gov.br/saude/pt-br/vacinacao/calendario e armazenada em data/scrap.txt. Se o arquivo não existir ou estiver vazio, o bot carrega automaticamente os dados mais recentes.

2. Personas e Dores Atendidas
👤 Personas
Mariana (Mãe de primeira viagem): Tem dificuldade em memorizar o calendário intenso de vacinas do bebê nos primeiros meses de vida.

Lucas (Jovem Adulto): Não sabe quais vacinas de reforço deve tomar após sair da idade escolar.

Sr. José (Idoso): Busca um canal direto para saber sobre doses específicas para sua idade sem navegar em sites complexos.

Clara (Gestante): Precisa de clareza sobre quais imunizantes são obrigatórios e seguros durante a gestação.

🩹 Dores que o Bot Resolve
Complexidade de Dados: O site oficial apresenta tabelas extensas; o bot filtra e entrega apenas o que é relevante para o perfil consultado.

Cálculo de Faixa Etária: Automatiza a conversão de "Data de Nascimento" para faixas de meses ou anos, evitando erros de interpretação do usuário.

Acessibilidade: Transforma uma busca técnica em uma conversa intuitiva, facilitando o acesso à saúde pública.

3. Iniciando
Abra o Telegram.

Busque por @Gotinha_bot ou escaneie o QrCode abaixo.

<p align="center">
<img src="assets/img/qr-code-telegram.png" alt="QR Code do bot" width="220" />
</p>

Digite /start ou /help.

Bot exibirá teclado com opções principais: Início, Vacinas, Help.

4. Fluxo principal de uso
4.1 Menu inicial
Início: mensagem de boas-vindas e instruções rápidas.

Help: link de suporte (https://LinkDoSite).

Vacinas: início da consulta de imunização.

4.2 Consulta por Grupo
Clique em Vacinas.

Escolha Grupo.

Selecione um dos grupos de pesquisa:

Crianca (todas as idades da categoria infantil)

Adolescente

Adulto

Idoso

Gestante

O bot responde com calendário e todas as vacinas listadas por período.

4.3 Consulta por Idade (Data de Nascimento)
Clique em Vacinas.

Selecione Idade.

Informe data de nascimento no formato DD/MM/AAAA.

O bot calcula idade em dias/meses/anos e identifica o grupo mais apropriado:

crianca (0 a ~15 meses ou 4-14 anos, com subfaixas de meses/anos)

adolescente (9 a 24 anos, mapeando faixas específicas)

adulto (25 a 59 anos)

idoso (60+ anos)

A resposta traz o calendário filtrado, com vacina, dose e período.

5. Resultado esperado
Depois de qualquer consulta o bot devolve:

Título identificando o grupo (💉 CALENDÁRIO: ...).

Periodização clara (📍 [período]).

Lista de vacinas com doses, ex:

• Vacina X _Dose única_

Mensagens de erro/tratamento:

⚠️ Nenhuma informação encontrada para esta categoria.

❌ Erro ao acessar o site do Ministério da Saúde.

Formato inválido! Use DD/MM/AAAA.

6. Observações do usuário
O bot precisa estar em execução para responder às mensagens.

Use formato de data válido: DD/MM/AAAA.

Se o resultado for vazio, tente outra alternativa (Grupo ou Idade).

Aguarde até alguns segundos para o retorno, pois o sistema processa os dados internos antes de responder.

7. Exemplo de Uso
/start

Escolha Vacinas.

Escolha Idade ou Grupo.

Consulta por idade:

Informe sua data de nascimento, por exemplo: 25/08/2016.

O bot retorna o grupo e as vacinas recomendadas para a faixa etária.

Consulta por grupo:

Escolha Adolescente, Adulto, Idoso, etc.

Saída típica:

💉 CALENDÁRIO: CRIANÇA

📍 2 meses

• BCG _Dose única_

• Hepatite B _1ª dose_

Manual de Instalação
A seguir, o passo a passo completo para instalar e executar o bot localmente.

1.1 Requisitos mínimos
Python 3.9 ou superior instalado

Conexão de internet ativa

Token do bot do Telegram (BOT_TOKEN) (criado com o BotFather)

1.2 Instalação
Clone o repositório:

Bash
git clone https://github.com/PI-Nexus/Projeto-Integrador-I.git
cd Projeto-Integrador-I
Instale as dependências (deve ter pip instalado):

Bash
pip install -r requirements.txt
Configure o token do bot no arquivo .env na raiz:

Ini, TOML
TOKEN_BOT=seu_token_aqui
PORT=8080
Crie a pasta de dados caso ainda não exista:

Bash
mkdir data
1.3 Executando
Bash
python main.py
Verifique no console se aparece: Bot iniciando....

1.4 Teste rápido
No Telegram, abra @Gotinha_bot.

Envie /start.

Selecione Vacinas e escolha Grupo ou Idade.

1.5 Problemas comuns
telebot.apihelper.ApiTelegramException → token inválido ou firewall.

ModuleNotFoundError → ambiente virtual não ativado ou dependências faltando.

FileNotFoundError: data/scrap.txt → execute o script scrap.py.

Conclusão
O bot tem como objetivo facilitar o acesso às informações sobre vacinação de forma simples, rápida e acessível através da interface do Telegram.