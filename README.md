# Assitente de dados públicos da saúde para vacinação

## Tema do Semestre: 
Desenvolvimento de Aplicação com Lógica Algorítmica em Análise de Dados (sem Persistência de Dados)

## Conhecimentos Ensinados
- Elaborar Documentação de Software (artefatos de processo ágil; manual do produto);
- Empregar Processo de Desenvolvimento Ágil – Scrum (adaptação da API);
- Desenvolver solução computacional usando Lógica Algorítmica.


# Descrição do Desafio
Desenvolver um assistente virtual que use dados de portais públicos oficiais de saúde sobre vacinação para informar o cidadão sobre calendário para diferentes faixas etárias (crianças, adultos, idosos...), coberturas vacinais em diferentes regiões brasileiras e demais informações sobre o tema disponíveis (integrar com plataformas altamente usadas como telegram, usar linguagem natural para a interação além de comandos e até voz como uma alexa são grandes diferenciais. Mas ressalta-se que tudo isso precisa ser feito através de programação sem utilizar APIs externas)

# Índice
* [Equipe](#Equipe)
* [Objetivo do Projeto](#objetivo-do-projeto)
* [Backlog do produto](#Backlog-do-Produto)
* [Registro das Sprints](#Registro-das-Sprints)

# Equipe
|    Função     | Nome                                  |                                                                                                                                                      LinkedIn & GitHub                                                                                                                                                      |
| :-----------: | :------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Product Owner |   Natan Telles         |     [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/natan-telles-5b2970288) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/natan-telles)              |
| Scrum Master  | Davi Couto |      [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/davi-couto-do-nascimento-7604343a6/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/DaviCouto-gd)     |
| Team Member   | Daniel Oliveira              |         [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/daniel-oliveira-alexandre-753a063bb) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/oliveiraalexandredaniel-lgtm)        |
|  Team Member  | Eduardo Cabral                 |         [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/eduardo-vital-cabral-529499312/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/edu-cabral)        |
|  Team Member  | Enzo Francisquetto                 |   [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/enzofrancisquetto-018377356) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/francisquettoenzo)   |
|  Team Member  | Isaac Ferraz       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/isaacferraz1311) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/isaac-ferraz)   | 
|  Team Member  | Leonardo Gabriel       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/leonardo-gabriel-dos-santos-79b848329) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/Leonardo-gabsantos) |
|  Team Member  | Renan Ramos       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/renan-ramos-a520662a2) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/renandevcode) |
|  Team Member  | Yago Moraes       |           [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/yago-moraes) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/YagoRGM) 

# Objetivo do Projeto
O objetivo do projeto é desenvolver um assistente virtual que use dados de portais públicos de saúde sobre vacinação, visando:
- Informar o usuário sobre vacinas e seus calendários com base na faixa etária/grupo (crianças, adolescentes, adultos, idosos e gestantes);
- Trazer coberturas vacinais para diferentes regiões brasileiras;
- Outras informações relacionadas ao tema.

O foco do projeto é o algoritmo, sem o uso de persistência de dados (Banco de Dados).

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

# Backlog do Produto
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


Manual do Usuário: [Clique aqui para abrir o manual](docs/Manual%20do%20Usuário.md) 
