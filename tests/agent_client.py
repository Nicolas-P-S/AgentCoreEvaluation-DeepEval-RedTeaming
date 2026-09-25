import json
import os
import uuid
import boto3
from botocore.exceptions import EventStreamError
from dotenv import load_dotenv

load_dotenv()  # carrega as variáveis do arquivo .env, se existir

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

# ARN do harness — pode vir do .env (AGENT_RUNTIME_ARN=...) ou ser colado direto aqui.
AGENT_RUNTIME_ARN = os.environ.get(
    "AGENT_RUNTIME_ARN",
    "arn:aws:bedrock-agentcore:us-east-2:721563685419:runtime/harness_harness_nova_lite_games-FJTsGb6POV",
)

# As credenciais (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
# são lidas automaticamente pelo boto3 a partir das variáveis de ambiente
# carregadas do .env — não é preciso passá-las explicitamente aqui.
_client = boto3.client("bedrock-agentcore", region_name=REGION)

# Prefixo usado para marcar respostas que falharam na invocação, sem lançar
# exceção — assim quem chama pode detectar e pular o caso, em vez de derrubar
# a coleta inteira dos testes.
ERRO_AGENTE_PREFIXO = "[ERRO_AGENTE]"


def nova_sessao():
    """Gera um session id válido (o AgentCore exige um id razoavelmente longo)."""
    return str(uuid.uuid4()) + str(uuid.uuid4())  # garante tamanho mínimo


def invocar_pixel(mensagem: str, session_id: str) -> str:
    """
    Envia uma mensagem ao Pixel através do Harness do AgentCore e retorna o
    texto da resposta.

    Em caso de falha durante o streaming (ex: limite de tokens do modelo
    estourado, erro de runtime), NÃO lança exceção — retorna uma string
    marcada com o prefixo ERRO_AGENTE_PREFIXO, para que o chamador possa
    detectar e pular esse caso sem derrubar toda a execução.
    """
    try:
        response = _client.invoke_harness(
            harnessArn=AGENT_RUNTIME_ARN,
            qualifier="DEFAULT",
            runtimeSessionId=session_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": mensagem
                        }
                    ]
                }
            ],
        )

        partes = []

        for evento in response["stream"]:
            if "contentBlockDelta" in evento:
                delta = evento["contentBlockDelta"].get("delta", {})

                if "text" in delta:
                    partes.append(delta["text"])

        return "".join(partes)

    except EventStreamError as e:
        print(f"[AVISO] Erro de streaming ao invocar o agente: {e}")
        return f"{ERRO_AGENTE_PREFIXO} Falha de streaming (possível limite de tokens): {e}"

    except Exception as e:
        print(f"[AVISO] Erro inesperado ao invocar o agente: {e}")
        return f"{ERRO_AGENTE_PREFIXO} Erro inesperado: {e}"


if __name__ == "__main__":
    # Teste rápido e isolado do cliente
    sid = nova_sessao()
    resposta = invocar_pixel("Quanto custa o Grand Theft Auto IV: The Complete Edition?", sid)
    print("Resposta do Pixel:")
    print(resposta)