# The ARK download tracker (Cloudflare Worker)

Counts GitHub-release downloads for The ARK across the canonical
repository, other branches, and forks. Forks are identified by GitHub
`owner/repo`.

Homepage is an **isolated counter**: the number is on the download
button. Nobody reports a download. The click is the count.

GET `/download` **serves** the tarball via `env.ASSETS.fetch`. It does
not 302 to GitHub. `Cache-Control: private, no-store`.

`totalKey()` = `ark|__total__`. PROJECT `ark`. Worker
`ark-download-tracker`. KV namespace `ARK_DOWNLOADS` bound as
`DOWNLOADS`.

Additive human/bot keys sit **alongside** those totals:
`ark|__views_human__`, `ark|__views_bot__`, `ark|__downloads_human__`,
`ark|__downloads_bot__`. Legacy `views` / `downloads` are never reset.

### Human / bot split (Whitestone fleet canary)

Shared modules (copy into sibling trackers):

- `src/classify.js` — counted-GET classification
- `src/stats-shape.js` — additive `/stats` + `/count` shape

**Invariant:** `views === views_human + views_bot` (same for downloads).

**Legacy choice: derive the bot bucket on read.** When the split keys
start at 0, `/stats` and `/count` set `views_bot = views - views_human`
(and the same for downloads) so the invariant holds. Pre-split traffic
is attributed to the bot bucket **on read only**. This is not a one-time
KV rewrite and there is no `classification.legacy` field.

Classification on each counted GET:

1. Health-check UAs → bot
2. `cf.botManagement` `verifiedBot` or `score <= 30` → bot
3. UA denylist (Googlebot, bingbot, GPTBot, ClaudeBot, Bytespider,
   PetalBot, Yandex, Semrush, Ahrefs, DotBot, curl/wget/python-requests,
   CF-Healthchecks, …) → bot
4. Else human
5. If `botManagement` is missing: UA + health-check only.
   `classification.method` is `ua+healthcheck`. Never invent scores.

`classification` is `{ method, bot_score_threshold: 30, note }`.
`method` is `cf-bot-management+ua` only when `request.cf.botManagement`
is actually present.

No secrets belong in this directory.

Not a kernel. Local deniable vault. Hosted API never logs phrases and
never stores vault blobs. Forks are welcome and always allowed.

This worker is The ARK only. It is not mixed with AZ-OS, GodLock,
ForgeReceipts, Glossa Filter, AZ-CLCE, or any other product.

Isolated counter: Worker `ark-download-tracker`, project `ark`.

## Bindings

| Binding     | Type | Purpose |
|-------------|------|---------|
| `DOWNLOADS` | KV   | Counters keyed `project|owner|repo|branch|fork` |
| `AZIEL_RUNTIME` | service | Suite mesh `/v1/mesh/*` PROXY to aziel-runtime (HTTP fallback when unbound) |

KV id in `wrangler.toml`: `c7305a73417348f6ad41a3529f0d0235`.
Binding name MUST stay `DOWNLOADS` (not `ARK_DOWNLOADS` — that is
the Cloudflare namespace title).

## Routes

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/` | Isolated homepage: increment views, live counts on the page, Live Nodes strip. Rose-star brand mark top-left (`/sigil.png`, empty alt; not "everblooming sigil" wording). |
| GET | `/sigil.png` | Same-origin Aziel Eliab rose-star brand mark (Worker assets). |
| GET | `/download?repo=&tag=&asset=` | Increment downloads, serve the asset from `ASSETS` |
| GET | `/count` | JSON `{project, views, downloads, total}` plus additive `views_human` / `views_bot` / `downloads_human` / `downloads_bot`, `human{}`, `bot{}`, `classification{}` (reads KV; does not increment) |
| GET | `/stats` | JSON totals plus additive human/bot split plus per-repo and per-branch breakdown |
| POST | `/event` | A fork reports a download |
| GET | `/v1/mesh` · `/v1/mesh/status` | PROXY suite mesh status via `AZIEL_RUNTIME`. Default OFF. Never enables. QNS-CD-1.0 cross-map (no public qnsd proxy). |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence) |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. |

Tracked asset URL:

```
https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz
```

## CORS

All responses include `Access-Control-Allow-Origin: *`.

## AI runtime (`/v1`)

CORS `*`. `GET /v1/health`, `GET /v1/levels`, `POST /v1/sweep` `{b64|text}`,
`GET /openapi.json` (OpenAPI 3.1), `GET /ai`.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (`AZIEL_RUNTIME`). Default OFF.
QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a
hub cite / Worker mesh cross-map only (local qnsd in
[qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog
`mesh` field in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime);
pair custody on [AZInterface](https://github.com/AzielEliab/azinterface)).
Not a Softwares-tab product. No public qnsd proxy. No Node Gate. No auto-heal.
Not anonymity. Human UI Live Nodes strip polls `GET /v1/mesh`. Catalog MCP
`mesh_*` + FragGate `slug=mesh`. Full node process is local `qnm-node/`.
Routes under `/v1` **do not** increment download KV.
Sweep is Mode E heuristics only. No clamscan. Payload is not stored.
Do NOT add unlock/encrypt/decrypt that takes a passphrase.

Help page: `/ai`. Combined catalog: https://aziel-runtime.vibelock.workers.dev/

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import OpenAPI as a custom tool or GPT Action, or connect MCP. Always send `User-Agent: Mozilla/5.0`.
