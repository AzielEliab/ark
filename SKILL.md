---
name: The ARK
description: Use when calling The ARK hosted /v1 or installing the local package. Author Aziel Eliab.
---

# The ARK

Local deniable vault. “Rotating Kernel” means the rotating crypto/engine, not a Linux/Windows kernel. Not a bootable OS, not a worm, not hosted unlock. Author: Aziel Eliab.

**THIS IS:** a local deniable vault. Every phrase is a login. One phrase → one vault. Empty vault indistinguishable from a wrong phrase.

**THIS IS NOT:** a kernel, a bootable OS, a worm, kernel isolation, or hosted unlock. Hosted /v1 never stores phrases or vaults.

Author: **Aziel Eliab**. Forks are welcome and always allowed. Apache-2.0.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://ark-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://ark-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/levels` | Level list. Hosted never unlocks a vault. |
| POST | `/v1/sweep` | Advisory sweep preview. Hosted never stores phrases or vaults. |

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/levels
```

## Local (after one-click install)

```bash
curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash
ark ui
```

Then open http://127.0.0.1:8850 (loopback only).

DOI: https://doi.org/10.5281/zenodo.21435810  
Record: https://zenodo.org/records/21435810  

Counted download (gzip HTTP 200, no 302): https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/ark
