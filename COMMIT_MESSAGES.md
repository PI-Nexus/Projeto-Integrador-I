## Padrão de Mensagens de Commit

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