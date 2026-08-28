# Contributing to The ARK

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ARK_TEST_KDF=1 python -m pytest -q
```

Python 3.10+. Tests MUST set `ARK_TEST_KDF=1` so Argon2id uses 8 MiB / t=1.
Do not run tests against the 256–1024 MiB production profiles.

## Ground rules

1. **Not a kernel.** "Rotating Kernel" is the rotating crypto/engine, not
   Linux/Windows kernel isolation, not a bootable OS, not a worm.
2. **Local deniable vault.** Every phrase is a login. A wrong phrase
   silently creates/opens a different empty vault. Forgotten phrase =
   permanent loss.
3. **Do not add cloud unlock/encrypt/decrypt that takes a passphrase.**
   The hosted Worker never stores phrases or vault blobs.
4. **Do not print "950/1000 military-grade".** Civilian software. HSM,
   kernel isolation, and classified OS are out of scope.
5. **Virus sweep is a local intake filter** on files YOU put in YOUR
   vault, not a network AV product and not an exploit.
6. **UI binds loopback only** (`127.0.0.1:8850`). Do not listen on `0.0.0.0`.
7. **Do not merge this product into AZ-OS, GodLock, ForgeReceipts, or
   any sibling tree.** The ARK is standalone.
8. **Do not mix the download tracker** with any other product's Worker or KV.
9. New behavior needs a test that fails without the change.
10. Production Argon2id profiles stay as spec. Test profiles are env-gated.

## Where to change things

- Config / KDF profiles: `ark/config.py`
- Crypto: `ark/crypto/`
- Vault format: `ark/vault/`
- Engine: `ark/engine/`
- Mode E: `ark/security/virus.py`
- CLI: `ark/cli.py`
- Local UI: `ark/ui/`, `ark/web/`
- Spec: `docs/whitepaper.md`
- Source megalith: `docs/source/`
- Flutter: `mobile/`
- Isolated counter + hosted heuristics API: `workers/download-tracker/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Ship as Aziel Eliab.
