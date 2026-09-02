# The ARK (Aziel Rotating Kernel)

**Local deniable vault.** Every phrase is a login. One phrase → one vault.
Empty vault indistinguishable from a wrong phrase. AES-256-GCM, Argon2id,
HKDF subkeys, Mode E intake filter before encrypt, auto-lock + zeroization.

**Author:** Aziel Eliab
**Date:** 2026
**License:** [Apache-2.0](LICENSE)

> Not a kernel, not a bootable OS, not a worm, not kernel isolation.
> “Rotating Kernel” means the rotating crypto/engine, not a Linux/Windows kernel.

See the spec: [docs/whitepaper.md](docs/whitepaper.md). Source megalith and
design notes: [docs/source/](docs/source/). How to contribute:
[CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**


## One-click install

```bash
curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `ark ui`.

Or tap **Download** / **One-click install** on the Worker homepage
(a 6th-grader can tap it):
https://ark-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

# → [https://ark-download-tracker.vibelock.workers.dev/](https://ark-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted):
[ark-0.1.0.tar.gz](https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz)

- Live count JSON: [https://ark-download-tracker.vibelock.workers.dev/stats](https://ark-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://ark-download-tracker.vibelock.workers.dev/openapi.json](https://ark-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://ark-download-tracker.vibelock.workers.dev/v1/skill](https://ark-download-tracker.vibelock.workers.dev/v1/skill)
- One-click install: [https://ark-download-tracker.vibelock.workers.dev/install.sh](https://ark-download-tracker.vibelock.workers.dev/install.sh)
- GitHub: [https://github.com/AzielEliab/ark](https://github.com/AzielEliab/ark)

- DOI: [10.5281/zenodo.21435810](https://doi.org/10.5281/zenodo.21435810)
- Zenodo: [https://zenodo.org/records/21435810](https://zenodo.org/records/21435810)

Isolated counter: Worker `ark-download-tracker`, KV `ARK_DOWNLOADS`. Not mixed with any other product. `/v1` does not increment downloads.


## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
ark ui
```

Open http://127.0.0.1:8850 (loopback only). No CDN, no telemetry.

Counted download: [https://ark-download-tracker.vibelock.workers.dev/](https://ark-download-tracker.vibelock.workers.dev/)

Direct tarball (also counted): [ark-0.1.0.tar.gz](https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz)

GitHub: [https://github.com/AzielEliab/ark](https://github.com/AzielEliab/ark)

---

## Honest scope

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

```bash
ark version
ark ui                                          # 127.0.0.1:8850 loopback only
ark unlock --phrase ... --level normal          # or ARK_PHRASE; never printed
ark put FILE
ark get FILE_ID --out PATH
ark list
ark sweep FILE                                  # Mode E; does not store
ark lock                                        # CLI is one-shot; UI lock zeroizes
ark console                                     # optional tkinter; skip without DISPLAY
```

Phrase is `--phrase` or `ARK_PHRASE`. Never printed.

## UI

`ark ui` binds **127.0.0.1:8850** only. Phrase field, security level,
unlock, list, upload encrypt (multipart), download decrypt, sweep, lock.
Dark matte / gold. Banner: not a kernel. Self-contained CSS, no CDN, no
telemetry.

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
- `POST https://ark-download-tracker.vibelock.workers.dev/v1/sweep` `{b64}` or `{text}`
- OpenAPI 3.1: https://ark-download-tracker.vibelock.workers.dev/openapi.json
- Help: https://ark-download-tracker.vibelock.workers.dev/ai

`/v1` does not increment the download counter. Sweep does not store the payload.
Do not POST passphrases here.

One-URL catalog: https://aziel-runtime.vibelock.workers.dev/openapi.json

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
