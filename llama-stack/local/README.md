### Setup

[Dallas Summit Connect 2025 Slides](https://people.redhat.com/bkozdemb/downloads/llamastack_dallas_2025.pdf)

Install the [ollama model server](https://ollama.com/).

Install python library management tools.

```bash
pip install uv pipenv
```
Sync python env

```bash
pipenv sync
```
Set envs (do we need both LLAMA_STACK_MODEL and INFERENCE_MODEL)?

```bash
export LLAMA_STACK_MODEL="llama3.1:8b"
export INFERENCE_MODEL="llama3.1:8b"
export LLAMA_STACK_PORT=8321
export LLAMA_STACK_SERVER=http://localhost:$LLAMA_STACK_PORT
```

Run model

```bash
ollama run ${LLAMA_STACK_MODEL} --keepalive 120m
```
```bash
>>> hello
Hello! How are you today? Is there something I can help you with or would you like to chat?

>>> /bye
```
Start the Llama Stack Server.

```bash
podman run --name=llamastack --network=host \                   
  -d -p $LLAMA_STACK_PORT:$LLAMA_STACK_PORT \
  llamastack/distribution-ollama:0.2.9 \
  --port $LLAMA_STACK_PORT \
  --env INFERENCE_MODEL=$LLAMA_STACK_MODEL \
  --env OLLAMA_URL=http://localhost:11434
```

Start the MCP Weather Server.

```bash
podman run --name=mcp_weather --rm -d -p 3001:3001 quay.io/rh-aiservices-bu/mcp-weather:0.1.0-amd64
```

Register the MCP Server as a tool.

```bash
llama-stack-client toolgroups register --provider-id model-context-protocol --mcp-endpoint "http://localhost:3001/sse" mcp::weather
```

Run a check
```bash
llama-stack-client toolgroups list
```
```console
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ identifier             ┃ provider_id            ┃ args ┃ mcp_endpoint                                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ builtin::websearch     │ tavily-search          │ None │ None                                         │
│ builtin::rag           │ rag-runtime            │ None │ None                                         │
│ builtin::wolfram_alpha │ wolfram-alpha          │ None │ None                                         │
│ mcp::weather           │ model-context-protocol │ None │ McpEndpoint(uri='http://localhost:3001/sse') │
└────────────────────────┴────────────────────────┴──────┴──────────────────────────────────────────────┘
```
Run the examples

Basic RAG - This example uses a built-in RAG tool.
```bash
python3 01-basic-rag.py
```

Weather, Calculator Tools - This example uses a user defined calculator tool and interacts with an
MCP server to obtain weather info.
```bash
python 02-weather-calc-tools.py
```

Guardrails - Getting started with security.
```bash
python 03-guardrails.py
```

Adapted from: https://rh-aiservices-bu.github.io/llama-stack-tutorial
