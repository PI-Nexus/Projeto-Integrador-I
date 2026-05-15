tools = [

    {"type": "function",
"function": {
    "name": "servicos",
    "description": (
        "Fornece servicos disponiveis com botoes : 'Início','Vacinas','Cobertura Vacinal','Unidades próximas','FAQ' "
        "Para ver barra de servicos em botoes , semelhante ao menu "
    ),
    "parameters": {
        "type": "object",
        "properties": {}
            }
        }
    },
{"type": "function",
"function": {
    "name": "comandos",
    "description": (
        "É o primeiro serviço a enviar quando alguém entra, então cumprimentos e mensagens sem sentido podem retornar a função "
        "Primeira interação do usuário ou o reinicio das atiividades"
    ),
    "parameters": {
        "type": "object",
        "properties": {}
            }
        }
    }
    ,
    {
        "type": "function",
        "function": {
            "name": "pedir_localizacao",
            "description": (
                "Solicita a localização do usuário para gerar unidades de saúde próoxima onde ele possa se vacinar "
                "para encontrar UBS ou vacinas próximas"
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
                "fornece regiões para verificar a cobertura vacinal"
                "para ver cobertura vacinal da  regiao"
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
                "fornecer dashboard com dados de cobertura vacinal"
                "para ver um dashboard interativo das coberturas vacinais "
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
            "Use esta função quando o usuário informar ou quiser informar "
            "sua data de nascimento para consultar vacinas recomendadas, "
            "vacinas pendentes, calendário vacinal ou verificar sua situação vacinal. "
            "A data deve estar no formato DD/MM/AAAA."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_nascimento": {
                    "type": "string",
                    "description": (
                        "Data de nascimento do usuário no formato DD/MM/AAAA. "
                        "Exemplo: 25/12/2010"
                    )
                }
            },
            "required": ["data_nascimento"]
        }
    }
}
]
