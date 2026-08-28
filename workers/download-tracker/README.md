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

KV id in `wrangler.toml`: `c7305a73417348f6ad41a3529f0d0235`.
Binding name MUST stay `DOWNLOADS` (not `ARK_DOWNLOADS` — that is
the Cloudflare namespace title).

## Routes

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/` | Isolated homepage: live count on the download button |
| GET | `/download?repo=&tag=&asset=` | Increment KV, serve the asset from `ASSETS` |
| GET | `/count` | JSON `{project, total}` |
| GET | `/stats` | JSON totals plus per-repo and per-branch breakdown |
| POST | `/event` | A fork reports a download |

Tracked asset URL:

```
https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz
```

## CORS

All responses include `Access-Control-Allow-Origin: *`.

## AI runtime (`/v1`)

CORS `*`. `GET /v1/health`, `GET /v1/levels`, `POST /v1/sweep` `{b64|text}`,
`GET /openapi.json` (OpenAPI 3.1), `GET /ai`.
Routes under `/v1` **do not** increment download KV.
Sweep is Mode E heuristics only. No clamscan. Payload is not stored.
Do NOT add unlock/encrypt/decrypt that takes a passphrase.

Help page: `/ai`. Combined catalog: https://aziel-runtime.vibelock.workers.dev/
