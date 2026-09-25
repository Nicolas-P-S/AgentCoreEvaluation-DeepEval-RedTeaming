"""
run_agentcore_interactions.py

Frente A do desafio — AgentCore Evaluations.

Este script NÃO avalia nada sozinho. Ele só gera, de forma programática,
as interações reais do golden dataset contra o agente (via boto3), para que
elas fiquem registradas no CloudWatch/Transaction Search. A avaliação em si
(built-in + o avaliador customizado 'pixel-preco-com-ferramenta') é rodada
depois, no console do AgentCore, apontando para esses logs.

Uso:
    python run_agentcore_interactions.py
"""

import time

from dotenv import load_dotenv

load_dotenv()

from agent_client import invocar_pixel, nova_sessao
from test_cases import GOLDEN_DATASET


def rodar_caso(caso):
    session_id = nova_sessao()
    respostas = []

    for turno in caso["turnos"]:
        resposta = invocar_pixel(turno, session_id)
        respostas.append({"turno": turno, "resposta": resposta})
        time.sleep(1)  # pequena pausa para não sobrecarregar / facilitar leitura nos logs

    return respostas


def main():
    print(f"Rodando {len(GOLDEN_DATASET)} casos contra o agente...\n")

    for caso in GOLDEN_DATASET:
        print(f"--- Caso {caso['id']} ({caso['categoria']}) ---")
        respostas = rodar_caso(caso)
        for r in respostas:
            print(f"  > {r['turno']}")
            print(f"  < {r['resposta'][:200]}...\n")

    print("Concluído. As interações já devem estar disponíveis no CloudWatch "
          "(Transaction Search) em alguns minutos.")
    print("Próximo passo: no console AgentCore -> Avaliações -> Create batch "
          "evaluation, selecionando o agente e os avaliadores desejados.")


if __name__ == "__main__":
    main()