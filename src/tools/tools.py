tools = [
    {
        "type": "function",
        "function": {
            "name": "servicos",
            "description": (
                "USE APENAS quando o usuário solicitar explicitamente para ver as opções, "
                "exibir o menu principal, abrir a barra de botões ou pedir ajuda genérica do sistema."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "comandos",
            "description": (
                "USE APENAS no primeiríssimo contato absoluto do usuário ou se ele digitar explicitamente /start ou /help."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pedir_localizacao",
            "description": (
                "USE APENAS se o usuário pedir para encontrar um posto de saúde, "
                "procurar uma UBS próxima, ver onde se vacinar geograficamente ou pedir para compartilhar localização."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escolher_regiao",
            "description": (
                "USE APENAS quando o usuário quiser verificar dados estatísticos ou a cobertura vacinal de uma região ou estado do Brasil."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dashboard",
            "description": (
                "USE APENAS quando o usuário pedir especificamente para ver os gráficos, acessar o Power BI ou visualizar o painel interativo de dados."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "processar_dados",
            "description": (
                "USE APENAS quando o usuário fornecer explicitamente uma data de nascimento no formato DD/MM/AAAA para consultar o calendário vacinal dele."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "data_nascimento": {
                        "type": "string",
                        "description": "Data de nascimento do usuário no formato DD/MM/AAAA."
                    }
                },
                "required": ["data_nascimento"]
            }
        }
    }
]