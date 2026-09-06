---
name: The ARK
description: Use when calling The ARK hosted /v1 or installing the local package. Dual surface: Worker /v1 + GET /mcp, or aziel-runtime FragGate slug ark. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Author Aziel Eliab.
---

# The ARK

Local deniable vault. Not a kernel. Every phrase is a door. Author: **Aziel Eliab**.

**THIS IS:** a local deniable vault.

**THIS IS NOT:** a kernel, bootloader, hypervisor, or malware. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://ark-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker MCP pointer: `GET https://ark-download-tracker.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://ark-download-tracker.vibelock.workers.dev/v1/skill`
- Suite mesh PROXY: `GET https://ark-download-tracker.vibelock.workers.dev/v1/mesh` (default OFF)

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- `GET /v1/mesh` — PROXY suite mesh status. Default OFF. QNM live|locked|isolated. Never enables.
- `GET /v1/mesh/nodes` — PROXY Live Nodes roster
- `POST /v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` — PROXY. Bearer required to enable. No auto-heal.
- Product POSTs listed in OpenAPI

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import OpenAPI as a custom tool (Grok, Claude, Gemini, and similar), as a GPT Action in ChatGPT, or as HTTP tools (Venice and other HTTP-tool clients). Cursor and Glama: connect the catalog MCP. This Worker `/v1/mesh/*` PROXY to aziel-runtime via AZIEL_RUNTIME. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/mesh
```

## Local (after one-click install)

```bash
curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash
ark ui
ark doctor
```

Then open http://127.0.0.1:8850 (loopback only).

Counted download (gzip HTTP 200, no 302): https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/ark

Paper: DOI https://doi.org/10.5281/zenodo.21435810 · https://zenodo.org/records/21435810 · Apache-2.0. Forks welcome.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Mode E heuristics sweep. Not a kernel. Hosted never unlocks or stores vaults.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/ark/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://ark-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://ark-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://ark-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `ark doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF).

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a custom tool (Grok, Claude, Gemini, and similar), as a GPT Action in ChatGPT, or as HTTP tools (Venice and other HTTP-tool clients). Cursor and Glama: connect the catalog MCP. Suite mesh: `GET /v1/mesh` PROXY (default OFF). Catalog MCP `mesh_*` + FragGate `slug=mesh`.
