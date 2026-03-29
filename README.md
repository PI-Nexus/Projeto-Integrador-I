# Manual do Usuário — Bot de Vacinação

## 1. Visão Geral
O bot de vacinação (`@Gotinha_bot`) é um assistente Telegram para consulta rápida de calendários vacinais do Ministério da Saúde com base em:
- Seleção de grupo (Criança, Adolescente, Adulto, Idoso, Gestante)
- Pesquisa por data de nascimento (idade atual)

A base de dados é obtida via scraping de `https://www.gov.br/saude/pt-br/vacinacao/calendario` e armazenada em `data/scrap.txt`. Se o arquivo não existir ou estiver vazio, o bot carrega automaticamente os dados mais recentes.

---

## 2. Iniciando
1. Abra o Telegram.
2. Busque por `@Gotinha_bot` ou escaneie o QrCode abaixo.

<p align="center">
  <img src="assets/img/qr-code-telegram.png" alt="QR Code do bot" width="200" />
</p>

3. Digite `/start` ou `/help`.
4. Bot exibirá teclado com opções principais: `Início`, `Vacinas`, `Help`.

---

## 3. Fluxo principal de uso
### 3.1 Menu inicial
- `Início`: mensagem de boas-vindas e instruções rápidas.
- `Help`: link de suporte (`https://LinkDoSite`).
- `Vacinas`: início da consulta de imunização.

### 3.2 Consulta por Grupo
1. Clique em `Vacinas`.
2. Escolha `Grupo`.
3. Selecione um dos grupos de pesquisa:
   - `Crianca` (todas as idades da categoria infantil)
   - `Adolescente`
   - `Adulto`
   - `Idoso`
   - `Gestante`
4. O bot responde com calendário e todas as vacinas listadas por período.

### 3.3 Consulta por Idade (Data de Nascimento)
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

## 4. Resultado esperado
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

## 5. Observações do usuário
- O bot precisa estar em execução para responder às mensagens.
- Use formato de data válido: `DD/MM/AAAA`.
- Se o resultado for vazio, tente outra alternativa (`Grupo` ou `Idade`).
- Aguarde até alguns segundos para o retorno, pois o sistema processa os dados internos antes de responder.

---

## 6. Exemplo de Uso

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

## 8. Conclusão

O bot tem como objetivo facilitar o acesso às informações sobre vacinação de forma simples, rápida e acessível através da interface do Telegram.

### Padrão de Mensagens de Commit

| Tipo | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| **`<feat>`** | Adição de um novo recurso ou funcionalidade. | `feat (AB-1243, AB-56): Implementação dos repositories usados nas operações com as tabelas de variações climáticas` |
| **`<fix>`** | Correção de um erro (bug). | `fix (#45): Correção do componente de seleção de município` |
| **`<docs>`** | Atualização ou criação de documentação. | `docs (#45): inclusão de diagrama de modelo de BD para a aplicação` |
| **`<style>`** | Mudanças de formatação/estética que não afetam a lógica. | `style (AB-1243, AB-56): ajuste de nomes de variáveis para o padrão camelCase` |
| **`<refactor>`** | Refatoração de código que não altera a funcionalidade final. | `refactor (ID): limpeza de funções redundantes no controller` |
| **`<test>`** | Adiciona ou modifica testes. | `test (ID): criação de testes para validação de login` |
| **`<chore>`** | Atualizações menores que não impactam a funcionalidade. | `chore (ID): atualização de dependências do npm` |

---

**Estrutura do comando:** `git commit -m "<tipo> (<id_demanda1>, <id_demanda2>): <descrição da entrega>"`