# The ARK

A local vault for files on this computer. The phrase you choose is the login.

**Author:** Aziel Eliab  
**License:** [Apache-2.0](LICENSE)

## Start

1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Open the vault

```bash
ark ui
```

3. Go to http://127.0.0.1:8850/ and enter a phrase.

`ark` alone prints these next steps. `ark --help` lists commands. `ark doctor` checks this copy.

**Forks are welcome and always allowed.**

One-click install (counted tarball, then the same `ark ui` step):

```bash
curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash
```

Counted download: [https://ark-download-tracker.vibelock.workers.dev/](https://ark-download-tracker.vibelock.workers.dev/)

Direct tarball: [ark-0.1.0.tar.gz](https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz)

GitHub: [https://github.com/AzielEliab/ark](https://github.com/AzielEliab/ark)

See [docs/whitepaper.md](docs/whitepaper.md), [docs/source/](docs/source/), and [CONTRIBUTING.md](CONTRIBUTING.md).

## Notes

- **Not a kernel, not a bootable OS, not a worm, not kernel isolation.**
  “Rotating Kernel” means the rotating crypto/engine.
- Local deniable vault. Forgotten phrase = permanent loss. Weak phrase =
  isolated vault compromise. Does not defeat live OS compromise while unlocked.
- Civilian software. Remaining gap in the paper (HSM, kernel isolation,
  classified OS) is explicitly out of scope. Do not treat this as
  military-grade.
- Virus sweep is a **local intake filter** on files YOU put in YOUR vault,
  not a network AV product and not an exploit.
- Empty / wrong-phrase vaults: `open_or_create` always succeeds. If no
  header matches, ARK creates a new vault. That **is** deniability: a
  wrong phrase silently creates/opens a different empty vault.
- Pi cycle 3-1-4 and Phoenix (destroy / reseed / rebuild) are
  **application-layer mixing** of storage blocks and decoys. They are not
  an extra cryptographic assumption beyond AES-GCM + Argon2id + HKDF.
- Standalone from AZ-OS, GodLock, ForgeReceipts.
- Loopback UI, no telemetry. Hosted API never logs phrases and never
  stores vault blobs.

## Engine

- AES-256-GCM
- Argon2id profiles (normal 256 MiB t=3, strong 512 MiB t=4, paranoid
  1024 MiB t=4). Tests use `ARK_TEST_KDF=1` (8 MiB, t=1) only.
- HKDF-SHA256 subkeys `ARK:ENC` / `ARK:META` / `ARK:LOG` / `ARK:FILE`
- Uniform failure message: `Unlock/decrypt failed.`
- Mode E sweep before encrypt (PE/ELF/Mach-O, powershell -enc, curl|sh)
- Data dir: `./ARK_DATA` under cwd (or `--data`). Never a cloud vault.

## Install

Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## CLI

People see short text. Scripts pass `--json`.

```bash
ark
ark ui
ark doctor
ark version
ark unlock --phrase ... --level normal
ark put FILE
ark get FILE_ID --out PATH
ark list
ark lock
ark sweep FILE
ark console
```

`sweep` and `console` are the advanced commands. Phrase is `--phrase` or `ARK_PHRASE`. Never printed.

## UI

`ark ui` binds **127.0.0.1:8850** only and prints `Open http://127.0.0.1:8850/`.
The first screen asks for a phrase and offers **Open vault**. Lock timing, the intake check, and JSON import/export sit under **Advanced**. Scope notes sit under **About**.
Light and dark follow the system. Focus is gold. Self-contained CSS, no CDN, no telemetry.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.ark`.
Offline. No analytics. Dark matte / gold.

Phrase field, security level, list placeholder. Banner: the crypto engine
is the desktop package; this app is the dome UI.

```bash
cd mobile
flutter create --org com.azieeliab --project-name ark .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you
run `flutter create .` (this machine has no Flutter SDK on PATH). Then open
`android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a
store listing.

Counted desktop download: [https://ark-download-tracker.vibelock.workers.dev/](https://ark-download-tracker.vibelock.workers.dev/)

**Forks are welcome and always allowed.**

## Tests

```bash
pip install -e ".[dev]"
ARK_TEST_KDF=1 python -m pytest -q
```

Tests use a tmp data dir and tiny Argon2id. They must not use 256–1024 MiB
profiles. Offline. pytest is the dev extra.

## Worker

Isolated download counter for this project only. Worker
`ark-download-tracker`, project `ark`, KV `ARK_DOWNLOADS` bound as
`DOWNLOADS`. GET `/download` **serves** `ark-0.1.0.tar.gz` (does not 302
to GitHub). See [workers/download-tracker/README.md](workers/download-tracker/README.md).

Counted downloads (number on the button, no user reporting):
[https://ark-download-tracker.vibelock.workers.dev/](https://ark-download-tracker.vibelock.workers.dev/)

Hosted `/v1` is heuristics-only (health, levels, Mode E sweep). It never
stores phrases or vaults. There is no cloud unlock/encrypt/decrypt.

## Layout

```
ark/                  library (config, crypto, vault, engine, cli, ui)
ark/web/              loopback UI
tests/                pytest
docs/whitepaper.md    spec (honest scope)
docs/source/          megalith + design notes
mobile/               Flutter iPhone + Android (`flutter create .`)
workers/download-tracker/   Cloudflare Worker
```

## AI runtime

Not a kernel. Local deniable vault. Hosted API never logs phrases.

- `GET https://ark-download-tracker.vibelock.workers.dev/v1/health`
- `GET https://ark-download-tracker.vibelock.workers.dev/v1/levels`
- `GET https://ark-download-tracker.vibelock.workers.dev/v1/mesh` (PROXY; default OFF; QNS-CD-1.0 cross-map)
- `POST https://ark-download-tracker.vibelock.workers.dev/v1/sweep` `{b64}` or `{text}`
- OpenAPI 3.1: https://ark-download-tracker.vibelock.workers.dev/openapi.json
- Help: https://ark-download-tracker.vibelock.workers.dev/ai

`/v1` does not increment the download counter. Sweep does not store the payload.
Do not POST passphrases here.

One-URL catalog: https://aziel-runtime.vibelock.workers.dev/openapi.json

## Use with AI assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.

Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
This Worker skill: https://ark-download-tracker.vibelock.workers.dev/v1/skill
This Worker OpenAPI: https://ark-download-tracker.vibelock.workers.dev/openapi.json

Import the catalog or Worker OpenAPI as a custom tool (Grok, Claude, Gemini, and similar), as a GPT Action in ChatGPT (no auth), or as HTTP tools (Venice and other HTTP-tool clients). Cursor and Glama: connect the catalog MCP. This Worker `/v1/mesh/*` PROXY via `AZIEL_RUNTIME`. Humans use the complete Worker UI (Live Nodes strip). Dual surface: do not gut the human UI. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (local qnsd in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog `mesh` field in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair custody on [AZInterface](https://github.com/AzielEliab/azinterface)). Not a Softwares-tab product. No public qnsd proxy. No Node Gate. No auto-heal. Not anonymity. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Anon-broadcast is not a publish path. Always send `User-Agent: Mozilla/5.0`.

## Cite this

Aziel Eliab. The ARK. https://github.com/AzielEliab/ark. https://ark-download-tracker.vibelock.workers.dev. https://doi.org/10.5281/zenodo.21435810.

- Catalog: https://aziel-runtime.vibelock.workers.dev/
- Worker homepage: https://ark-download-tracker.vibelock.workers.dev/
- Counted download (gzip HTTP 200, no 302): https://ark-download-tracker.vibelock.workers.dev/download
- GitHub: https://github.com/AzielEliab/ark
- Citation JSON: https://ark-download-tracker.vibelock.workers.dev/cite.json
- DOI: https://doi.org/10.5281/zenodo.21435810

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
