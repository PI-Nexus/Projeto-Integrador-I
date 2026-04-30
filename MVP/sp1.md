# 📌 MVP - Gotinha BOT

## 🎯 Objetivo do MVP

O MVP da primeira sprint consiste em disponibilizar um **chatbot funcional** capaz de informar, de forma simples e personalizada, **quais vacinas são recomendadas para o usuário com base apenas na sua data de nascimento e perfil (gestante, bebê, adulto ou idoso)**.

Nesta primeira versão, o bot deverá:

- Receber a **data de nascimento** do usuário
- Identificar automaticamente a **faixa etária correta (meses/anos)**
- Considerar **perfis específicos** (gestante, bebê, adulto, idoso)
- Consultar uma base simplificada do calendário vacinal
- Retornar **apenas as vacinas relevantes** para aquele perfil, em linguagem clara

O objetivo central deste MVP é **eliminar a complexidade de leitura das tabelas oficiais**, transformando a busca por informações de vacinação em uma **interação conversacional rápida, acessível e sem margem para erro de interpretação**.

---

## 📝 Descrição da Solução
Será desenvolvido um bot no Telegram capaz de consultar uma base de dados gerada por scraping do portal oficial do Ministério da Saúde e, a partir disso, responder ao usuário quais vacinas são recomendadas para sua faixa etária ou grupo selecionado.

**Funcionalidades principais incluídas**
- Consulta por **grupo etário**
- Consulta por **data de nascimento**
- Cálculo automático de idade em meses/anos
- Resposta formatada com vacinas, doses e períodos

**Limitações conhecidas**
- Não possui banco de dados
- Não armazena histórico do usuário
- Não envia notificações (fora do escopo da sprint)

**Escopo Reduzido**
- Transformar tabelas complexas em respostas conversacionais personalizadas.

---

## 👥 Personas / Usuários-Alvo

- **Mariana (Mãe de primeira viagem):** dificuldade em acompanhar o calendário intenso do bebê
- **Lucas (Jovem adulto):** não sabe quais reforços vacinais precisa tomar
- **Sr. José (Idoso):** quer acesso simples sem navegar em sites complexos
- **Clara (Gestante):** precisa saber quais vacinas são seguras e obrigatórias

---

## 🔑 User Stories (Backlog do MVP)

| ID  | User Story                                                                 | Prioridade | Estimativa |
|-----|-----------------------------------------------------------------------------|------------|------------|
| US1 | Como paciente, desejo obter informação de fácil acesso sobre vacinas.      | Alta       | 5 pontos   |
| US2 | Como responsável, quero consultar as vacinas do meu filho pela idade.     | Alta       | 5 pontos   |

---

## 🏅 DoR - Definition of Ready <a id="dor"></a>

|             Critério             | Descrição                                                                                         |
| :------------------------------: | ------------------------------------------------------------------------------------------------- |
|       Clareza na Descrição       | A User Story está escrita no formato “Como [persona], quero [ação] para que [objetivo]”.         |
| Critérios de Aceitação Definidos | A história possui critérios claros como: consulta por idade ou grupo e retorno das vacinas.     |
| Cenários de Teste Especificados  | A história possui cenários como: cálculo de idade e exibição correta das vacinas.                |
|           Independente           | A história pode ser implementada sem depender de outras tarefas da Sprint.                       |
|    Compreensão Compartilhada     | A equipe entende o fluxo: usuário → entrada (idade/grupo) → resposta (vacinas).                  |
|            Estimável             | A história foi estimada considerando cálculo de idade e consulta à base de dados.                |
|       Documentos de Apoio        | Estrutura dos dados de vacinas e exemplos de respostas estão disponíveis.                        |
|   Critérios técnicos acordados   | Definido uso de scraping e regras para cálculo de idade (meses/anos).                            |

---

## 🏅 DoD - Definition of Done <a id="dod"></a>

|                 Critério                 | Descrição                                                                                  |
| :--------------------------------------: | ------------------------------------------------------------------------------------------ |
|     Critérios de Aceitação atendidos     | Consulta por idade e grupo retorna corretamente as vacinas esperadas.                      |
|        Testes manuais realizados         | Testes confirmam cálculo correto da idade e resposta adequada do bot.                      |
|             Código revisado              | O código foi revisado por pelo menos um membro da equipe.                                  |
|     Documentação interna atualizada      | MVP e funcionamento do bot foram documentados.                                             |
|  Integração com outras partes testadas   | Integração com scraping e processamento de dados validada.                                 |
| Build/Testes automatiados (se aplicável) | O sistema funciona sem falhas após implementação das funcionalidades.                      |
|             Validação do PO              | O Product Owner validou as respostas do bot conforme o calendário vacinal.                 |
|            Pronto para deploy            | Funcionalidade está estável e utilizável no Telegram.                                      |

---

## 📅 Sprint(s) Relacionadas
| Sprint | Entregas Principais                                  | Status     |
|--------|-------------------------------------------------------|------------|
| 01     | Consulta por grupo, consulta por idade, cálculo etário| Concluído  |

---

## 📊 Critérios de Aceitação
- O usuário deve conseguir consultar vacinas por **grupo** ou **data de nascimento**
- O sistema deve calcular corretamente a faixa etária
- O bot deve retornar lista organizada com **vacina, dose e período**
- O fluxo completo deve funcionar dentro do Telegram sem falhas

---

## 📈 Métricas de Validação
- Testes funcionais realizados pela equipe
- Tempo médio de resposta do bot
- Validação manual das informações retornadas com o calendário oficial

---

## 🚀 Próximos Passos
- Implementar sistema de notificações de próximas vacinas
- Adicionar consulta de cobertura vacinal por região
- Melhorar usabilidade e comandos do bot

---

## 📂 Anexos / Evidências

**Vídeo de Demonstração:**\
Confira o bot em funcionamento:
https://youtube.com/shorts/9Sdsh29rDXo?si=FZLqHO0BJC0KCYis