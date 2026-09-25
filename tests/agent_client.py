import json
import os
import uuid
import boto3
from botocore.exceptions import EventStreamError
from dotenv import load_dotenv

load_dotenv() 

REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

AGENT_RUNTIME_ARN = os.environ.get(
    "AGENT_RUNTIME_ARN",
    "arn:aws:bedrock-agentcore:us-east-2:721563685419:runtime/harness_harness_nova_lite_games-FJTsGb6POV",
)

_client = boto3.client("bedrock-agentcore", region_name=REGION)

ERRO_AGENTE_PREFIXO = "[ERRO_AGENTE]"

def nova_sessao():
    return str(uuid.uuid4()) + str(uuid.uuid4())


def invocar_pixel(mensagem: str, session_id: str) -> str:
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
    sid = nova_sessao()
    resposta = invocar_pixel("Quanto custa o Grand Theft Auto IV: The Complete Edition?", sid)
    print("Resposta do Pixel:")
    print(resposta)