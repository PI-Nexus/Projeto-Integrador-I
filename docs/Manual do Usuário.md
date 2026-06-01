# Manual do Usuário — Bot de Vacinação

## 1. Visão Geral
O bot de vacinação (`@Gotinha_bot`) é um assistente Telegram para consulta rápida de calendários vacinais do Ministério da Saúde com base em:
- Seleção de grupo (Criança, Adolescente, Adulto, Idoso, Gestante)
- Pesquisa por data de nascimento (idade atual)

A base de dados é obtida via scraping de `https://www.gov.br/saude/pt-br/vacinacao/calendario` e armazenada em `data/scrap.txt`. Se o arquivo não existir ou estiver vazio, o bot carrega automaticamente os dados mais recentes.

---

## 2. Personas e Dores Atendidas

### 👤 Personas
* **Mariana (Mãe de primeira viagem):** Tem dificuldade em memorizar o calendário intenso de vacinas do bebê nos primeiros meses de vida.
* **Lucas (Jovem Adulto):** Não sabe quais vacinas de reforço deve tomar após sair da idade escolar.
* **Sr. José (Idoso):** Busca um canal direto para saber sobre doses específicas para sua idade sem navegar em sites complexos.
* **Clara (Gestante):** Precisa de clareza sobre quais imunizantes são obrigatórios e seguros durante a gestação.
* **Beatriz (Universitária/Estudante da área da saúde):** Quer entender os componentes ou a justificativa técnica de uma vacina específica (ex: a diferença entre a vacina da Gripe trivalente e quadrivalente) sem ter que ler artigos acadêmicos longos.
* **Rodrigo (Pai preocupado com reações):** O filho tomou a vacina de 2 meses e está com o braço vermelho e um pouco de febre. Ele precisa de uma orientação rápida e calma sobre se isso é normal ou se deve ir ao hospital.
* **Dona Sônia (Leiga digital):** Tem medo de fake news que recebe no WhatsApp sobre vacinas e quer um canal confiável para perguntar, em linguagem simples, se "tal vacina realmente funciona".

### 🩹 Dores que o Bot Resolve
* **Complexidade de Dados:** O site oficial apresenta tabelas extensas; o bot filtra e entrega apenas o que é relevante para o perfil consultado.
* **Cálculo de Faixa Etária:** Automatiza a conversão de "Data de Nascimento" para faixas de meses ou anos, evitando erros de interpretação do usuário.
* **Acessibilidade:** Transforma uma busca técnica em uma conversa intuitiva, facilitando o acesso à saúde pública.
Falta de Contexto e Explicação: Antes, o bot mostrava apenas o nome da vacina. Agora, a IA explica o que a vacina previne, reações comuns e orientações pós-vacina em tempo real.
* **Medo de Efeitos Colaterais (Ansiedade):** O bot atua como um primeiro filtro de suporte emocional e informativo, explicando sintomas comuns (como febre baixa ou dor no local da aplicação) para evitar pânico.
* **Linguagem Muito Técnica:** Transforma termos médicos complexos do Ministério da Saúde em respostas simples, diretas e acessíveis para qualquer cidadão.
* **Barreira de Consultas Rígidas:** O usuário não precisa mais seguir apenas botões estruturados; ele pode conversar textualmente com o bot para tirar dúvidas livres sobre imunização.

---

## 3. Iniciando
1. Abra o Telegram.
2. Busque por `@Gotinha_bot` ou escaneie o QrCode abaixo.

<p align="center">
  <img src="../assets/img/qr-code-telegram.png" alt="QR Code do bot" width="220" />
</p>

3. Digite `/start` ou `/help`.
4. Bot exibirá teclado com opções principais: `Início`, `Vacinas`, `Help`.

---

## 4. Fluxo principal de uso
### 4.1 Menu inicial
- `Início`: mensagem de boas-vindas e instruções rápidas.
- `Vacinas`: Exibe todas as vacinas ao usuário com base na idade(Data de nascimeno ou faixa etária), o usuário seleciona as vacinas que ele deseja tomar e o bot enviará notificação por email perto do dia da vacina para lembrar o usuário.
- `Cobertura vacinal`: O usuário tem acesso aos dados da cobertura vacinal, sendo eles divididos em estado, município, ranking de estados, e um dashboard interativo que permite um grande campo de possibilidades de análises de informações relacionados as vacinas (filtro por Região, Estado, Data, Cidades).
- `Unidades próximas`: O usuário fornece a localização para o bot via gps e o bot retorna as unidades de saúde mais proximas da posição atual do cidadão.
- `FAQ`:Resolve dúvidas relacionadas às reações comuns e aos documentos necessários para levar no dia da vacinação.


### 4.2 Consulta por Grupo
1. Clique em `Vacinas`.
2. Escolha `Grupo`.
3. Selecione um dos grupos de pesquisa:
   - `Crianca` (todas as idades da categoria infantil)
   - `Adolescente`
   - `Adulto`
   - `Idoso`
   - `Gestante`
4. O bot responde com calendário e todas as vacinas listadas por período.

### 4.3 Consulta por Idade (Data de Nascimento)
1. Clique em `Vacinas`.
2. Selecione `Idade`.
3. Informe data de nascimento no formato `DD/MM/AAAA`.
4. O bot calcula idade em dias/meses/anos e identifica o grupo mais apropriado:
   - `crianca` (0 a ~15 meses ou 4-14 anos, com subfaixas de meses/anos)
   - `adolescente` (9 a 24 anos, mapeando faixas específicas)
   - `adulto` (25 a 59 anos)
   - `idoso` (60+ anos)
5. A resposta traz o calendário filtrado, com vacina, dose e período.

---

## 5. Resultado esperado
Depois de qualquer consulta na sessão vacinas, o bot devolve:
- Título identificando o grupo (`💉 CALENDÁRIO: ...`).
- Periodização clara (`📍 [período]`).
- Lista de vacinas com doses, ex:
  - `• Vacina X _Dose única_`

Mensagens de erro/tratamento:
- `⚠️ Nenhuma informação encontrada para esta categoria.`
- `❌ Erro ao acessar o site do Ministério da Saúde.`
- `Formato inválido! Use DD/MM/AAAA.`

---

## 6. Observações do usuário
- O bot precisa estar em execução para responder às mensagens.
- Use formato de data válido: `DD/MM/AAAA`.
- Se o resultado for vazio, tente outra alternativa (`Grupo` ou `Idade`).
- Aguarde até alguns segundos para o retorno, pois o sistema processa os dados internos antes de responder.
- Para acessar as unidades de saúde mais próximas, o gps do dispotivo precisa estar ativado para fornecer a localização ao bot.

---

## 7. Exemplo de Uso

**`/start`**
1. Escolha `Vacinas`.
2. Escolha `Idade` ou `Grupo`.

- Consulta por idade:
  - Informe sua data de nascimento, por exemplo: `25/08/2016`.
  - O bot retorna o grupo e as vacinas recomendadas para a faixa etária.
  - O usuário seleciona as vacinas que lhe interessa dentre a lista de vacinas que o bot forneceu
  - O bot pede o email do usuário e o usuário deve inserir, a fim de que receba notificações via email perto da data agendada para tomar a vacina.

- Consulta por grupo:
  - Escolha `Adolescente`, `Adulto`, `Idoso`, etc.
  - O bot retorna o grupo e as vacinas recomendadas para a faixa etária.
  - O usuário seleciona as vacinas que lhe interessa dentre a lista de vacinas que o bot forneceu
  - O bot pede o email do usuário e o usuário deve inserir, a fim de que receba notificações via email perto da data agendada para tomar a vacina.


Saída típica:
- `✅ Todas as vacinas foram agendadas com sucesso!`

---

## Manual de Instalação

A seguir, o passo a passo completo para instalar e executar o bot localmente.

### 1.1 Requisitos mínimos
- Python 3.9 ou superior instalado
- Conexão de internet ativa
- Token do bot do Telegram (`BOT_TOKEN`) (criado com o BotFather)

### 1.2 Instalação
1. Clone o repositório:
   ```bash
   git clone [https://github.com/PI-Nexus/Projeto-Integrador-I.git](https://github.com/PI-Nexus/Projeto-Integrador-I.git)
   cd Projeto-Integrador-
   
2. Após a clonagem do repositório, crie um arquivo .env dentro do repositório. 
   I
3. Dentro do arquivo .env, cole o token do seu bot criado pelo botfather

4. Por fim, execute o programa. Em caso de sucesso, no terminal aparecerá: "Bot gotinha iniciado com sucesso"
