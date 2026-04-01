## Objetivo do Projeto
O objetivo do projeto é desenvolver um assistente virtual que use dados de portais públicos de saúde sobre vacinação, visando:
- Informar o usuário sobre vacinas e seus calendários com base na faixa etária/grupo (crianças, adolescentes, adultos, idosos e gestantes);
- Trazer coberturas vacinais para diferentes regiões brasileiras;
- Outras informações relacionadas ao tema.

O foco do projeto é o algoritmo, sem o uso de persistência de dados (Banco de Dados).

---

## Equipe
|    Função     | Nome                                  |                                                                                                                                                      LinkedIn & GitHub                                                                                                                                                      |
| :-----------: | :------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Product Owner |   Natan Telles         |     [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/)              |
| Scrum Master  | Davi Couto |      [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/)     |
| Team Member   | Daniel Oliveira              |         [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/)        |
|  Team Member  | Eduardo Cabral                 |         [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/)        |
|  Team Member  | Enzo Francisquetto                 |   [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/)   |
|  Team Member  | Isaac Ferraz       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/)   | 
|  Team Member  | Leonardo Gabriel       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/) |
|  Team Member  | Renan Ramos       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/) |
|  Team Member  | Yago Moraes       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/) 

---

## Tecnologias

- Jira Software
- Git/Github
- Python
- Telegram
- Visual Studio
- Flask
- pyTelegramBotAPI
- BeautifulSoup
- Dotenv
- Requests

---
## Product Backlog
| Rank | Prioridade | User Story                                                                                                                                              | Estimativa | Sprint |
|------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|
| 1    | Alta       | Como paciente, desejo obter informação de fácil acesso à respeito de uma ou mais vacinas.| 5          | 1      |
| 2    | Alta       | Como parente de um paciente, gostaria de consultar as datas de vacinação para meu filho de 2 anos, para levá-lo na data correta e mantê-lo protegido contra doenças virais.                                                                    | 5          | 1      |                                                                                                                                                   | ...        | ...    |
| 3   | Média      | Como usuário do assistente virtual, gostaria de receber notificações perto da data da próxima vacina para não me esquecer.     | 8          | 2      |
| 4   | Média      | Como jornalista, gostaria de acessar os dados de cobertura vacinal da minha região para escrever uma matéria.    | 13          | 2      |
| 5   | Média      | Como cidadão, gostaria de poder utilizar comandos de voz para fazer buscas no assistente virtual    | 8          | 3      |
| 6   | Baixa      | Como adulto, gostaria de ver as possíveis dúvidas mais perguntadas sobre vacinações    | 3          | 3      |
| 7   | Baixa      | Como usuário do assistente, gostaria de consultar os postos de saúde próximos de mim    | 5          | 3      |
---

# Registro das Sprints

| Sprint            | Previsão   | Status   | Histórico |
|-------------------|------------|----------|-----------|
| 01                | 05/04/2026 | a fazer  | [MVP](MVP/sp1.md)  |
| 02                | 03/05/2026 | a fazer  | [a fazer]  |
| 03                | 31/05/2026 | a fazer  | [a fazer] |
| Feira de Soluções | 11/06/2026 | a fazer  | [a fazer] |


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

### 🩹 Dores que o Bot Resolve
* **Complexidade de Dados:** O site oficial apresenta tabelas extensas; o bot filtra e entrega apenas o que é relevante para o perfil consultado.
* **Cálculo de Faixa Etária:** Automatiza a conversão de "Data de Nascimento" para faixas de meses ou anos, evitando erros de interpretação do usuário.
* **Acessibilidade:** Transforma uma busca técnica em uma conversa intuitiva, facilitando o acesso à saúde pública.

---

## 3. Iniciando
1. Abra o Telegram.
2. Busque por `@Gotinha_bot` ou escaneie o QrCode abaixo.

<p align="center">
  <img src="assets/img/qr-code-telegram.png" alt="QR Code do bot" width="220" />
</p>

3. Digite `/start` ou `/help`.
4. Bot exibirá teclado com opções principais: `Início`, `Vacinas`, `Help`.

---

## 4. Fluxo principal de uso
### 4.1 Menu inicial
- `Início`: mensagem de boas-vindas e instruções rápidas.
- `Help`: link de suporte (`https://LinkDoSite`).
- `Vacinas`: início da consulta de imunização.

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
Depois de qualquer consulta o bot devolve:
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

---

## 7. Exemplo de Uso

**`/start`**
1. Escolha `Vacinas`.
2. Escolha `Idade` ou `Grupo`.

- Consulta por idade:
  - Informe sua data de nascimento, por exemplo: `25/08/2016`.
  - O bot retorna o grupo e as vacinas recomendadas para a faixa etária.

- Consulta por grupo:
  - Escolha `Adolescente`, `Adulto`, `Idoso`, etc.

Saída típica:
- `💉 CALENDÁRIO: CRIANÇA`
- `📍 2 meses`
- `• BCG _Dose única_`
- `• Hepatite B _1ª dose_`

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
   cd Projeto-Integrador-I
