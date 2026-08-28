# The ARK (Aziel Rotating Kernel) — v0.1 spec

**Author:** Aziel Eliab · **Date:** 2026 · **License:** Apache-2.0

This is the shipped product spec. The design paper in
[docs/source/ARK-structural-design.txt](source/ARK-structural-design.txt)
is philosophy. Where the paper and this spec disagree, this spec wins.

## What it is

A **local deniable vault**. Every phrase is a login. One phrase → one vault.
There are no usernames, accounts, vault registries, or selector UIs.

`open_or_create_vault` always succeeds. If no on-disk header’s verification
tag matches the phrase, ARK creates a new vault. That **is** deniability:
a wrong phrase silently creates/opens a different empty vault. An empty
vault is indistinguishable from a wrong-phrase vault.

## What it is not

- Not a kernel, not a bootable OS, not a worm, not kernel isolation.
- “Rotating Kernel” means the rotating crypto/engine, not Linux/Windows.
- Not a network antivirus product.
- Not a cloud vault. Data dir is `./ARK_DATA` (or `--data`).
- Standalone from AZ-OS, GodLock, ForgeReceipts.

## Cryptography (in scope)

- AES-256-GCM for payloads (`AAD = ARK:V1`)
- Argon2id for the master key (production: 256/512/1024 MiB)
- HKDF-SHA256 subkeys: `ARK:ENC`, `ARK:META`, `ARK:LOG`, `ARK:FILE`
- Uniform failure: `Unlock/decrypt failed.`
- Best-effort zeroization of `bytearray` key material on lock

## Application-layer mixing (not extra crypto)

Pi cycle **3-1-4**: each group of 8 storage blocks is permuted by
`(0 1 2)(3)(4 5 6 7)` — a 3-cycle, a 1-cycle, and a 4-cycle — then
inverted on decrypt. This is packing, not a new primitive.

Phoenix (destroy / reseed / rebuild): on put, ARK writes
level-dependent random decoy `.ark` files that are **not** in the
encrypted manifest (destroy-looking noise), seeded from `os.urandom`,
after the real ciphertext is 3-1-4 packed.

Security levels change **behavior** (auto-lock seconds, decoy count),
not the AES-GCM / Argon2id / HKDF construction.

## Mode E

Mandatory local intake filter **before encrypt**. Heuristics: PE/MZ,
ELF, Mach-O, `powershell -enc`, `curl|sh` / `wget|sh`, macro autoopen.
Optional local `clamscan` if present. If flagged, encryption is refused.
The payload is not stored. This is not an exploit and not a network AV.

The hosted Worker exposes the **same heuristics only**. No clamscan on
Cloudflare. No passphrase endpoints. No vault blobs in KV.

## Honest failure modes

- Forgotten phrase = permanent loss
- Weak phrase = isolated vault compromise
- Does not defeat live OS compromise while unlocked
- Python cannot guarantee perfect zeroization
- HSM, kernel isolation, and classified OS are out of scope

Civilian software. Do not claim military-grade scores.

## Auto-lock

| Level | Auto-lock | Decoys |
|-------|-----------|--------|
| normal | 15 min | 0 |
| strong | 5 min | 2 |
| paranoid | 60 s | 8 |

## UI / mobile

Desktop loopback HTTP on `127.0.0.1:8850`. Optional tkinter console.
Flutter `mobile/` is the dome UI; the crypto engine is the desktop
package. Offline. No telemetry.
