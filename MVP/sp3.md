# 📌 MVP - Gotinha BOT (Sprint 3)

## 🎯 Objetivo do MVP

O MVP da terceira sprint evolui a API integrando autenticação biométrica e inteligência artificial generativa, permitindo não apenas operações de segurança robusta, mas também respostas inteligentes e personalizadas baseadas em análise contextual.

Nesta versão, o bot deverá:

- Implementar autenticação por **biometria** (reconhecimento oral) para acesso **seguro**
- Integrar o **Ollama** para processamento de linguagem natural e geração de respostas contextualizadas
- Disponibilizar **consultas inteligentes** alimentadas por modelos de IA local
- Fornecer **análise de dados** com insights gerados automaticamente
- Permitir **interações conversacionais** baseadas em contexto do usuário

O objetivo central desta sprint é evoluir o sistema de um modelo reativo e estático para um modelo inteligente e adaptativo, onde a IA Ollama fornece respostas personalizadas baseadas em biometria e histórico, aumentando significativamente a segurança, inteligência e utilidade prática da API no dia a dia.

---

## 📝 Descrição da Solução

A API será expandida para incluir funcionalidades baseadas em **autenticação biométrica** e **inteligência artificial local com Ollama**, permitindo operações seguras e respostas inteligentes contextualizadas.

**Funcionalidades principais incluídas**
- Sistema de **autenticação biométrica** (reconhecimento facial/digital)
- Integração com **Ollama** para processamento de linguagem natural
- **Consultas inteligentes** geradas por IA baseadas em contexto do usuário
- **Análise de dados** com insights automáticos personalizados
- **Interações conversacionais** contextualizadas e seguras

**Limitações conhecidas**
- Processamento de IA local dependente de recursos computacionais disponíveis
- Modelos Ollama requerem download e armazenamento local prévio

**Escopo Reduzido**
- Integração inicial com modelos Ollama padrão, sem customização avançada

---

## 👥 Personas / Usuários-Alvo

- **Mariana (Mãe de primeira viagem):** deseja ser lembrada das próximas vacinas do bebê e receber alertas contextualizados por IA sobre saúde infantil
- **Lucas (Jovem adulto):** quer praticidade para encontrar postos de saúde próximos e consultar informações de vacinação com respostas inteligentes personalizadas
- **Sr. José (Idoso):** precisa de lembretes claros e biometria como autenticação segura para não esquecer vacinas importantes e acessar dados de saúde
- **Clara (Gestante):** quer acompanhar prazos corretamente com alertas preditivos gerados por IA sobre vacinação na gravidez e puerpério
- **Jornalista:** busca dados confiáveis de cobertura vacinal para reportagens, com análise automática de tendências por região

---

## 🔑 User Stories (Backlog do MVP)

| ID  | User Story                                                                 | Prioridade | Estimativa |
|-----|-----------------------------------------------------------------------------|------------|------------|
| US6 |Como cidadão, gostaria de poder utilizar comandos de voz para fazer buscas no assistente virtual.       | Alta       | 8 pontos   |
| US7 | Como adulto, gostaria de fazer consultas com o bot usando minhas próprias palavras      | Média      | 8 pontos   |

---

## 🏅 DoR - Definition of Ready ca id="dor"></a>

| Critério | Descrição |
|----------|-----------|
| Clareza na Descrição | A User Story está escrita no formato "Como [persona], gostaria de [ação] para que [objetivo]". |
| Critérios de Aceitação Definidos | A história possui critérios claros como: autenticação biométrica bem-sucedida, resposta da IA Ollama ou localização retornada. |
| Cenários de Teste Especificados | A história possui cenários como: biometria aceita, biometria rejeitada, resposta da IA gerada ou falha na integração Ollama. |
| Independente | A história pode ser desenvolvida separadamente (ex: autenticação biométrica, integração Ollama, consultas inteligentes). |
| Compreensão Compartilhada | A equipe entende o fluxo: usuário → autenticação biométrica → ação → resposta (IA, dados ou localização). |
| Estimável | A história foi estimada considerando integrações (biometria, Ollama, dados públicos e localização). |
| Documentos de Apoio | Fluxos de autenticação biométrica, exemplos de prompts Ollama ou estrutura dos dados de IA estão disponíveis. |
| Critérios técnicos acordados | Integrações com APIs de biometria, modelos Ollama locais e dados públicos foram definidas previamente. |

---

## 🏅 DoD - Definition of Done <a id="dod"></a>

| Critério | Descrição |
|----------|-----------|
| Critérios de Aceitação atendidos | Autenticação biométrica, integração Ollama, consultas inteligentes e localização funcionam conforme esperado. |
| Testes manuais realizados | Testes confirmam autenticação biométrica bem-sucedida e rejeitada, respostas da IA Ollama geradas corretamente e requisições de localização retornadas. |
| Código revisado | O código foi revisado por pelo menos três membros da equipe focando em segurança biométrica e prompts Ollama. |
| Documentação interna atualizada | Atualizações nos README, fluxos, exemplos de prompts Ollama e estrutura dos dados de IA estão documentadas. |
| Integração com outras partes testadas | API integrada corretamente com modelos Ollama locais, APIs de biometria e dados públicos de saúde. |
| Build/Testes automatizados (se aplicável) | O sistema permanece estável e sem falhas após novas implementações de biometria e IA. |
| Validação do PO | Product Owner validou autenticação biométrica, respostas inteligentes da IA e funcionalidades de localização. |
| Pronto para deploy | Funcionalidades testadas, estáveis e prontas para uso em ambiente de produção ou testes integrados. |

---

### 📊 Regras específicas da Sprint 3

**Interações com o Ollama**
- Todas as respostas da IA devem ser geradas localmente via Ollama, sem dependência de APIs externas
- Prompts enviados ao Ollama devem incluir contexto do usuário (perfil, histórico, localização)
- Fallback configurado caso haja problemas na comunicação com a IA

**interações por biometria (comandos de voz)**
- Autenticação biométrica deve ser validada antes de qualquer operação sensível
- Suportar reconhecimento facial e reconhecimento de voz como métodos de autenticação
- Taxa de aceito mínima: 90% em condições normais de iluminação/áudio
- Dados biométricos não devem ser armazenados em texto plano (apenas hashes/templates)
- Falhas de autenticação biométrica permitem um número determinado de tentativas antes de bloqueio temporário

---

## 📅 Sprint(s) Relacionadas

| Sprint | Entregas Principais | Status |
|--------|-------------------|--------|
| 01 | Consulta por idade e grupo | Concluído |
| 02 | Notificações, cobertura vacinal, busa por postos de saúde | Concluído |
| 03 | Autenticação biométrica, integração Ollama, consultas inteligentes | Concluído |

---

## 📊 Critérios de Aceitação

- O usuário deve conseguir **autenticar-se via biometria (voz)**
- O sistema deve processar consultas através do **Ollama com respostas contextualizadas**
- O usuário deve conseguir consultar **recomendações de IA baseadas em perfil e histórico**
- O usuário deve conseguir visualizar dados no **dashboard com insights gerados por IA**
- O usuário deve conseguir encontrar **postos de saúde próximos com análise inteligente**
- Todas as funcionalidades devem funcionar dentro do **Telegram e API REST**

---

## 📈 Métricas de Validação

- Taxa de sucesso na autenticação biométrica: >= 90%
- Precisão das recomendações de IA avaliada por feedback do usuário
- Disponibilidade da API: >= 99%
- Satisfação do usuário com respostas inteligentes: >= 4.0/5.0

---

## 📂 Anexos / Evidências

**Vídeo de Demonstração:**\
Confira o bot em funcionamento (em andamento): ...
