# 📌 MVP - Gotinha BOT (Sprint 2)

## 🎯 Objetivo do MVP

O MVP da segunda sprint expande as funcionalidades do chatbot, adicionando **recursos proativos e contextuais**, permitindo não apenas consultas, mas também **alertas e informações baseadas na localização do usuário**.

Nesta versão, o bot deverá:

- Enviar **notificações próximas às datas de vacinação**
- Disponibilizar e filtrar os **dados de cobertura vacinal por diferentes regiões**
- Oferecer um **Dashboard interativo** de cobertura vacinal
- Permitir a consulta de **postos de saúde próximos ao usuário**

O objetivo central desta sprint é evoluir o sistema de um modelo **reativo (responde perguntas)** para um modelo **proativo e informativo**, aumentando o engajamento e a utilidade prática do bot no dia a dia.

---

## 📝 Descrição da Solução

Será expandido o bot do Telegram para incluir funcionalidades baseadas em **tempo e localização**, além da integração com dados públicos de saúde.

**Funcionalidades principais incluídas**
- Sistema de **notificações de vacinas futuras**
- Consulta de **cobertura vacinal por região**
- **Dashboard interativo** para visualização de dados
- Busca de **postos de saúde próximos**

**Limitações conhecidas**
- Notificações podem depender de execução contínua do bot (sem sistema robusto de filas)
- Dados de cobertura vacinal atualizados dependem de **fontes públicas do Ministério da Saúde**

**Escopo Reduzido**
- Introdução de comportamento proativo e geolocalização básica no bot.

---

## 👥 Personas / Usuários-Alvo

- **Mariana (Mãe de primeira viagem):** deseja ser lembrada das próximas vacinas do bebê
- **Lucas (Jovem adulto):** quer praticidade para encontrar postos de saúde próximos
- **Sr. José (Idoso):** precisa de lembretes para não esquecer vacinas importantes
- **Clara (Gestante):** quer acompanhar prazos corretamente
- **Jornalista:** busca dados confiáveis de cobertura vacinal para reportagens

---

## 🔑 User Stories (Backlog do MVP)

| ID  | User Story                                                                 | Prioridade | Estimativa |
|-----|-----------------------------------------------------------------------------|------------|------------|
| US3 | Como usuário, quero receber notificações antes das próximas vacinas.       | Alta       | 8 pontos   |
| US4 | Como jornalista, quero acessar dados de cobertura vacinal por região.      | Média      | 8 pontos   |
| US5 | Como usuário, quero encontrar postos de saúde próximos de mim.             | Alta       | 8 pontos   |

---


## 🏅 DoR - Definition of Ready <a id="dor"></a>

|             Critério             | Descrição                                                                                         |
| :------------------------------: | ------------------------------------------------------------------------------------------------- |
|       Clareza na Descrição       | A User Story está escrita no formato “Como [persona], gostaria de [ação] para que [objetivo]”.         |
| Critérios de Aceitação Definidos | A história possui critérios claros como: envio de notificações, consulta regional ou localização.|
| Cenários de Teste Especificados  | A história possui cenários como: notificação enviada, dados exibidos ou localização retornada.   |
|           Independente           | A história pode ser desenvolvida separadamente (ex: notificações, dashboard, postos).            |
|    Compreensão Compartilhada     | A equipe entende o fluxo: usuário → ação → resposta (alerta, dados ou localização).              |
|            Estimável             | A história foi estimada considerando integrações (dados públicos, localização, Telegram).        |
|       Documentos de Apoio        | Fluxos, exemplos de respostas ou estrutura dos dados de cobertura estão disponíveis.             |
|   Critérios técnicos acordados   | Integrações com interfaces/dados públicos e uso de localização foram definidos previamente.            |

---

## 🏅 DoD - Definition of Done <a id="dod"></a>

|                 Critério                 | Descrição                                                                                  |
| :--------------------------------------: | ------------------------------------------------------------------------------------------ |
|     Critérios de Aceitação atendidos     | Notificações, dashboard, cobertura e busca de postos funcionam conforme esperado.         |
|        Testes manuais realizados         | Testes confirmam envio de notificações, exibição correta dos dados e retorno por localização. |
|             Código revisado              | O código foi revisado por pelo menos três membros da equipe.                                  |
|     Documentação interna atualizada      | Atualizações feitas no MVP, fluxos e funcionamento das novas funcionalidades.              |
|  Integração com outras partes testadas   | Bot integrado corretamente com dados públicos e funcionalidades de localização.            |
| Build/Testes automatiados (se aplicável) | O sistema permanece estável e sem falhas após as novas implementações.                     |
|             Validação do PO              | O Product Owner validou notificações, dashboard e consultas.                               |
|            Pronto para deploy            | Funcionalidades testadas, estáveis e prontas para uso no Telegram.                         |

---

### 📊 Regras específicas da Sprint 2

**Notificações**
- Usuário consegue ativar o recebimento
- Sistema envia alerta com antecedência mínima definida

**Cobertura vacinal**
- Permite consulta por diferentes regiões
- Retorna dados organizados e compreensíveis

**Dashboard**
- Apresenta visualização clara dos dados
- Permite leitura fácil das informações de cobertura vacinal

**Postos de saúde**
- Retorna locais próximos com base na localização
- Apresenta informações úteis (nome, endereço ou referência)

---

## 📅 Sprint(s) Relacionadas
| Sprint | Entregas Principais                                           | Status     |
|--------|---------------------------------------------------------------|------------|
| 01     | Consulta por idade e grupo                                    | Concluído  |
| 02     | Notificações, cobertura vacinal, busca por postos de saúde    | Concluído  |

---

## 📊 Critérios de Aceitação
- O usuário deve conseguir **receber notificações de vacinas futuras**
- O sistema deve alertar o usuário com antecedência mínima
- O usuário deve conseguir consultar **cobertura vacinal por diferentes regiões**
- O usuário deve conseguir visualizar dados no **dashboard interativo**
- O usuário deve conseguir encontrar **postos de saúde próximos**
- Todas as funcionalidades devem funcionar dentro do Telegram

---

## 📈 Métricas de Validação
- Taxa de envio de notificações com sucesso
- Precisão dos dados para consultas
- Tempo de resposta para cobertura vacinal
- Feedback dos usuários sobre utilidade das notificações

---

## 🚀 Próximos Passos
- Implementar **comandos por voz**
- Melhorar interpretação com **linguagem natural (NLP)**
- Permitir **perguntas abertas sobre vacinação**
- Aprimorar sistema de notificações com maior personalização

---

## 📂 Anexos / Evidências
- Prints das interações no Telegram
- Exemplos de notificações enviadas
- Resultados de consultas por região
- Demonstração da busca por postos próximos