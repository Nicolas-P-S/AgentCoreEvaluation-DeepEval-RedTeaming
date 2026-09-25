# PIXEL — Evaluation & Red Teaming

Projeto de **avaliação, testes de segurança e red teaming de agentes de IA**, desenvolvido a partir do agente **Pixel**, um assistente virtual voltado para informações relacionadas à plataforma Steam.

O projeto combina avaliações automatizadas com **DeepEval**, avaliações do **Amazon Bedrock AgentCore Evaluations** e testes manuais de **Red Teaming**, buscando identificar problemas como alucinação, comportamento fora de escopo, vazamento de informações internas, prompt injection, jailbreak e uso inadequado de ferramentas.

---

## 📌 Sobre o projeto

O Pixel é um agente baseado no **Amazon Nova 2 Lite**, executado através do **Amazon Bedrock AgentCore**.

O agente possui acesso a ferramentas externas para consultar informações da Steam, incluindo:

* Preços e descontos de jogos;
* Requisitos de sistema;
* Políticas de suporte da Steam;
* Recomendações de jogos;
* Informações obtidas através de ferramentas e fontes externas.

A avaliação foi estruturada em três frentes principais:

1. **DeepEval** — avaliação automatizada das respostas;
2. **Amazon Bedrock AgentCore Evaluations** — avaliação das interações reais do agente;
3. **Red Teaming manual** — tentativa deliberada de induzir comportamentos inadequados.

O objetivo não é apenas verificar se o agente responde corretamente, mas também avaliar **segurança, confiabilidade, aderência ao domínio e resistência a ataques**.

---

# 🧪 O que foi avaliado

A avaliação considerou diferentes categorias de risco.

| Categoria                   | Objetivo                                                       |
| --------------------------- | -------------------------------------------------------------- |
| Consulta direta             | Verificar respostas sobre jogos e Steam                        |
| Uso de ferramentas          | Verificar se o agente utiliza as ferramentas corretamente      |
| Multi-turno                 | Avaliar comportamento ao longo de várias mensagens             |
| Fora de escopo              | Verificar se o agente recusa assuntos não relacionados à Steam |
| Prompt Injection            | Tentar alterar o comportamento do agente                       |
| Jailbreak                   | Tentar contornar as instruções do agente                       |
| Vazamento de informação     | Tentar obter informações internas                              |
| Promessas indevidas         | Induzir o agente a fazer afirmações não verificadas            |
| Uso indevido de ferramentas | Tentar manipular o uso das ferramentas                         |

Entre os principais problemas identificados durante a avaliação estiveram:

* Alucinação de informações;
* Vazamento de sintaxe interna de chamadas de ferramentas;
* Vazamento de raciocínio interno;
* Respostas fora do domínio;
* Inconsistência de idioma sob pressão adversarial.

---

# 🏗️ Arquitetura

A arquitetura utilizada no projeto é composta pelos seguintes elementos:

```text
                    ┌──────────────────────┐
                    │      Usuário         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Pixel Agent      │
                    │  Amazon Nova 2 Lite │
                    └──────────┬───────────┘
                               │
                    Amazon Bedrock AgentCore
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │ consultarPreco   │        │ consultarPolitica│
       │      Jogo        │        │      Steam       │
       └────────┬─────────┘        └─────────┬────────┘
                │                            │
                ▼                            ▼
        Steam Public API              Knowledge Base
                                      / RAG + S3
```

### Componentes principais

**Amazon Nova 2 Lite**

Modelo utilizado pelo agente.

**Amazon Bedrock AgentCore**

Responsável pela execução e gerenciamento do agente.

**AWS Lambda — `consultarPrecoJogo`**

Consulta informações de jogos através da API pública da Steam.

A implementação possui mecanismos de busca aproximada (*fuzzy matching*) para lidar com:

* nomes incompletos;
* abreviações;
* erros de digitação;
* buscas por palavras.

**AWS Lambda — `consultarPoliticaSteam`**

Consulta informações armazenadas em uma Knowledge Base contendo políticas da Steam.

**Amazon Bedrock AgentCore Gateway**

Expõe as ferramentas para o agente através de targets Lambda.

**Amazon CloudWatch**

Utilizado para observabilidade e análise das interações realizadas pelo agente.

---

# 📊 Estratégia de avaliação

O projeto utiliza duas abordagens automatizadas complementares.

## DeepEval

O mesmo conjunto de testes é executado localmente utilizando `pytest` e DeepEval.

As principais métricas utilizadas são:

* **Answer Relevancy**
* **Faithfulness**
* **G-Eval — Conformidade de Domínio**
* **RecusaApropriada**, criada especificamente para avaliar respostas de recusa.

Os thresholds definidos foram:

| Métrica                 | Threshold |
| ----------------------- | --------: |
| Faithfulness            |     ≥ 0,8 |
| Answer Relevancy        |     ≥ 0,7 |
| Conformidade de Domínio |     ≥ 0,8 |

---

## Amazon Bedrock AgentCore Evaluations

As interações são executadas contra o agente real e registradas no CloudWatch.

São utilizados avaliadores integrados, como:

* Faithfulness;
* Helpfulness;
* Goal Success Rate.

Também foi criado um avaliador personalizado:

```text
pixel-preco-com-ferramenta
```

Esse avaliador verifica especificamente se preços apresentados pelo agente possuem uma chamada real da ferramenta correspondente.

---

# 🔴 Red Teaming

Além das avaliações automatizadas, foram realizados testes manuais de Red Teaming.

Foram testadas técnicas relacionadas a:

* Prompt Injection;
* Jailbreak;
* Extração do System Prompt;
* Vazamento de informações internas;
* Vazamento de chamadas de ferramentas;
* Tentativas de obtenção de raciocínio interno;
* Manipulação de preços;
* Promessas indevidas;
* Uso inadequado das ferramentas;
* Mudança de idioma.

Os testes foram utilizados para identificar comportamentos que poderiam não ser capturados adequadamente por métricas tradicionais.

---

# 📁 Estrutura do projeto

```text
PIXEL-Evaluation-RedTeaming/
│
├── docs/
│   └── Documentação complementar
│
├── evidences/
│   └── Evidências dos testes e avaliações
│
├── resultados/
│   └── deepeval/
│       └── Resultados das avaliações DeepEval
│
├── tests/
│   └── Casos e scripts utilizados durante os testes
│
├── .gitignore
├── README.md
└── agradecimentos.md
```

> A estrutura pode receber novos arquivos e diretórios conforme novas avaliações forem adicionadas ao projeto.

---

# ⚙️ Requisitos

Para executar as avaliações locais, é necessário ter instalado:

### Software

* **Python 3.11+**
* **Git**
* **pip**
* **DeepEval**
* **pytest**

Para a execução das avaliações que interagem diretamente com a infraestrutura AWS, também são necessários:

* Conta AWS;
* Credenciais AWS configuradas;
* Permissões IAM adequadas;
* Amazon Bedrock com acesso aos recursos utilizados;
* AgentCore configurado;
* Recursos Lambda e Gateway configurados;
* Acesso aos logs do CloudWatch.

> A infraestrutura AWS do agente não é criada automaticamente por este repositório. O projeto pressupõe que o agente Pixel e seus recursos AWS já estejam configurados.

---

# 🚀 Como executar

## 1. Clonar o repositório

```bash
git clone https://github.com/Nicolas-P-S/PIXEL-Evaluation-RedTeaming.git
```

Entrar no diretório:

```bash
cd PIXEL-Evaluation-RedTeaming
```

---

## 2. Criar um ambiente virtual

### Windows

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.venv\Scripts\Activate.ps1
```

Caso esteja utilizando Git Bash:

```bash
source .venv/Scripts/activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Atualizar o pip

```bash
python -m pip install --upgrade pip
```

---

## 4. Instalar as dependências

Instale as dependências necessárias:

```bash
pip install deepeval pytest boto3
```

Caso o projeto possua um arquivo `requirements.txt`, prefira:

```bash
pip install -r requirements.txt
```

---

# 🔐 Configuração da AWS

As avaliações que utilizam o AgentCore precisam acessar recursos da AWS.

A forma recomendada é configurar as credenciais através do AWS CLI.

Verifique se o AWS CLI está instalado:

```bash
aws --version
```

Configure suas credenciais:

```bash
aws configure
```

Informe:

```text
AWS Access Key ID
AWS Secret Access Key
Default region name
Default output format
```

Depois, valide:

```bash
aws sts get-caller-identity
```

Se o comando retornar os dados da identidade AWS, as credenciais estão configuradas corretamente.

### ⚠️ Segurança

**Nunca coloque Access Keys diretamente no código ou no Git.**

Não faça:

```python
AWS_ACCESS_KEY_ID = "minha-chave"
AWS_SECRET_ACCESS_KEY = "minha-chave-secreta"
```

Também não envie arquivos contendo credenciais para o GitHub.

Utilize:

* AWS CLI;
* variáveis de ambiente;
* IAM Roles;
* ou outro mecanismo seguro de credenciais.

---

# 🧪 Executando os testes DeepEval

Com o ambiente virtual ativado, execute a suíte:

```bash
deepeval test run tests/test_*.py -v
```

Caso os testes estejam concentrados em um arquivo específico:

```bash
deepeval test run tests/<arquivo>.py -v
```

Também é possível utilizar o pytest diretamente quando a configuração do teste não depender do executor do DeepEval:

```bash
pytest -v
```

---

# ☁️ Executando avaliações do AgentCore

As avaliações do AgentCore dependem da infraestrutura AWS configurada para o Pixel.

O fluxo geral é:

```text
Golden Dataset
      │
      ▼
Script de execução
      │
      ▼
Amazon Bedrock AgentCore
      │
      ▼
Interações com o agente
      │
      ▼
CloudWatch
      │
      ▼
AgentCore Evaluations
      │
      ▼
Resultados
```

As interações devem ser executadas contra o agente real e posteriormente avaliadas utilizando os recursos disponíveis no AgentCore Evaluations.

> Os nomes dos recursos, região AWS, Agent Runtime, Gateway e demais identificadores dependem da configuração da conta AWS utilizada no projeto.

---

# 🧪 Golden Dataset

O projeto utiliza um conjunto de **20 casos de teste**, considerando os turnos individualmente.

Os casos abrangem:

* consultas diretas;
* tarefas que exigem ferramentas;
* conversas multi-turno;
* solicitações fora de escopo;
* entradas adversariais.

Cada caso possui critérios esperados para permitir a avaliação automatizada.

---

# 📈 Resultados — Baseline

Na avaliação inicial realizada com DeepEval:

**6 de 20 casos foram aprovados — 30%.**

| Categoria             | Casos | Aprovados |
| --------------------- | ----: | --------: |
| Consulta direta       |     3 |         1 |
| Tarefa com ferramenta |     2 |         2 |
| Multi-turno           |     8 |         2 |
| Fora de escopo        |     3 |         0 |
| Adversarial           |     4 |         1 |

Um dos problemas identificados foi uma alucinação relacionada à política de reembolso da Steam.

Também foi identificado vazamento da sintaxe interna utilizada para chamada de ferramenta.

---

# 🔴 Resultados do Red Teaming

Foram realizadas **15 tentativas manuais**.

O resultado inicial foi:

```text
13 / 15 resistências
86,7%
```

As principais vulnerabilidades encontradas foram:

| Vulnerabilidade                                  | Severidade |
| ------------------------------------------------ | ---------- |
| Vazamento de sintaxe interna de tool call        | Alta       |
| Vazamento de raciocínio interno                  | Alta       |
| Inconsistência de idioma sob pressão adversarial | Baixa      |

---

# 🔧 Correções implementadas

Após os testes, foram realizadas correções no agente.

### Vazamento de tool call

Foi adicionada uma regra específica proibindo a exposição da sintaxe interna das ferramentas ao usuário.

### Vazamento de raciocínio interno

Foi adicionada uma regra impedindo que deliberações ou meta-comentários internos fossem apresentados na resposta final.

### Busca de jogos

A Lambda responsável pela consulta de jogos recebeu melhorias de fuzzy matching para lidar melhor com nomes incompletos, abreviações e erros de digitação.

### Idioma

Foi adicionada uma regra reforçando que o agente deve responder no idioma utilizado pelo usuário.

### Respostas fora de escopo

Foi criada a métrica:

```text
RecusaApropriada
```

Essa métrica é aplicada especificamente aos casos em que o comportamento esperado é uma recusa.

### Informações provenientes do RAG

O agente recebeu instruções mais rígidas para não completar lacunas da Knowledge Base utilizando informações externas não verificadas.

---

# 🔄 Retestes

Devido ao limite orçamentário de **US$ 25**, não foi possível executar novamente toda a suíte completa de DeepEval e AgentCore Evaluations.

Como alternativa, os dois problemas considerados mais críticos foram retestados individualmente:

1. Vazamento de sintaxe interna de tool call;
2. Vazamento de raciocínio interno.

Nos retestes realizados após as correções, não houve reincidência desses dois comportamentos.

Também foram realizados testes adicionais envolvendo:

* nomes de jogos abreviados;
* nomes com erros de digitação;
* políticas da Steam;
* consultas relacionadas ao domínio do agente.

Esses testes apresentaram comportamento consistente com o esperado.

> Os retestes isolados não substituem uma nova execução completa da suíte. Eles servem como evidência de validação específica das correções implementadas.

---

# 📚 Documentação

Materiais complementares podem ser encontrados nos diretórios:

```text
docs/
evidences/
resultados/
```

Esses diretórios contêm documentação, evidências e resultados utilizados durante o processo de avaliação.

---

# 🛡️ Considerações de segurança

Este projeto possui finalidade de **avaliação e segurança de agentes de IA**.

Os testes de Red Teaming são utilizados para identificar vulnerabilidades e melhorar os mecanismos de proteção do agente.

Ao reproduzir os testes:

* utilize apenas sistemas sob sua autorização;
* não utilize credenciais reais de terceiros;
* não exponha chaves ou tokens nos arquivos;
* evite armazenar informações sensíveis nas evidências;
* utilize ambientes controlados para experimentação.

---

# 👤 Autor

**Nicolas Pereira de Souza**

Projeto desenvolvido como parte de estudos e atividades relacionadas a:

* Inteligência Artificial;
* LLM Evaluation;
* AI Safety;
* Red Teaming;
* AWS Bedrock;
* AgentCore;
* DeepEval;
* Engenharia de Software.

---

# 🙏 Agradecimentos

Agradecimentos e referências adicionais estão disponíveis em:

```text
agradecimentos.md
```

---
