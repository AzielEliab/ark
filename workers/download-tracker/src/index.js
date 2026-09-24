import * as engine from "./engine.js";
import { classifyRequest } from "./classify.js";
import {
  classificationBlock,
  incrementSplitKey,
  isStatsMetaKey,
  readSplitCounters,
  shapeCount,
  shapeStats,
  splitKeys,
} from "./stats-shape.js";
import {
  isMeshPath,
  meshOpenApiPaths,
  meshPointer,
  runMeshProxy,
} from "./mesh.js";
const EXAMPLE_PAYLOAD = {
  "text": "hello world"
};

const SKILL_MARKDOWN = "---\nname: The ARK\ndescription: Use when calling The ARK hosted /v1 or installing the local package. Dual surface: Worker /v1 + GET /mcp, or aziel-runtime FragGate slug ark. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer (hub cite / Worker mesh cross-map only; no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity. Author Aziel Eliab.\n---\n\n# The ARK\n\nLocal deniable vault. \u201cRotating Kernel\u201d means the rotating crypto/engine, not a Linux/Windows kernel. Not a bootable OS, not a worm, not hosted unlock. Author: Aziel Eliab.\n\n**THIS IS:** a local deniable vault. Every phrase is a login. One phrase \u2192 one vault. Empty vault indistinguishable from a wrong phrase.\n\n**THIS IS NOT:** a kernel, a bootable OS, a worm, kernel isolation, or hosted unlock. Hosted /v1 never stores phrases or vaults.\n\nAuthor: **Aziel Eliab**. Forks are welcome and always allowed. Apache-2.0.\n\nAlways send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.\n\n## Call these URLs\n\n- Worker OpenAPI: https://ark-download-tracker.vibelock.workers.dev/openapi.json\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- This Worker MCP pointer: `GET https://ark-download-tracker.vibelock.workers.dev/mcp`\n- Live skill (this markdown): `GET https://ark-download-tracker.vibelock.workers.dev/v1/skill`\n- Suite mesh PROXY: `GET https://ark-download-tracker.vibelock.workers.dev/v1/mesh` (default OFF)\n\nOps (do **not** increment downloads or views):\n\n| Method | Path | What |\n|--------|------|------|\n| GET | `/v1/health` | Liveness. Does not increment downloads. |\n| GET | `/v1/skill` | This markdown. Does not increment downloads. |\n| GET | `/v1/levels` | Level list. Hosted never unlocks a vault. |\n| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live\\|locked\\|isolated. QNS-CD-1.0 cross-map. Never enables. No public qnsd proxy. |\n| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). |\n| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |\n| POST | `/v1/sweep` | Advisory sweep preview. Hosted never stores phrases or vaults. |\n\nWorks with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import OpenAPI as a custom tool (Grok, Claude, Gemini, and similar), as a GPT Action in ChatGPT, or as HTTP tools (Venice and other HTTP-tool clients). Cursor and Glama: connect the catalog MCP. This Worker `/v1/mesh/*` PROXY to aziel-runtime via AZIEL_RUNTIME. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer (hub cite / Worker mesh cross-map only; local qnsd in qnm-node; no public proxy). No Node Gate. No auto-heal. Not anonymity.\n\n## Example\n\n```bash\ncurl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/health\ncurl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/skill\ncurl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/levels\ncurl -s -A 'Mozilla/5.0' https://ark-download-tracker.vibelock.workers.dev/v1/mesh\n```\n\n## Local (after one-click install)\n\n```bash\ncurl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash\nark ui\n```\n\nThen open http://127.0.0.1:8850 (loopback only).\n\nDOI: https://doi.org/10.5281/zenodo.21435810  \nRecord: https://zenodo.org/records/21435810  \n\nCounted download (gzip HTTP 200, no 302): https://ark-download-tracker.vibelock.workers.dev/download?asset=ark-0.1.0.tar.gz\nGitHub: https://github.com/AzielEliab/ark\n\n## Catalog + local UI\n\nAuthor: **Aziel Eliab**. Honest scope: Mode E heuristics sweep. Not a kernel. Hosted never unlocks or stores vaults.\n\n- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/ark/\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- This Worker skill: `GET https://ark-download-tracker.vibelock.workers.dev/v1/skill`\n- This Worker OpenAPI: https://ark-download-tracker.vibelock.workers.dev/openapi.json\n- Sample payload: `GET https://ark-download-tracker.vibelock.workers.dev/v1/example`\n\nLocal UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `ark doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). QNS-CD-1.0 is a hub cite / Worker mesh cross-map only — not a Softwares-tab product.\n\nWorks with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a custom tool (Grok, Claude, Gemini, and similar), as a GPT Action in ChatGPT, or as HTTP tools (Venice and other HTTP-tool clients). Cursor and Glama: connect the catalog MCP. Suite mesh: `GET /v1/mesh` PROXY (default OFF). Catalog MCP `mesh_*` + FragGate `slug=mesh`.\n";
/**
 * The ARK download tracker (Cloudflare Worker).
 *
 * GET  /        increments views (KV ark|__views__) + views_human|views_bot
 * GET  /download increments downloads, serves tarball via env.ASSETS.fetch (no 302)
 * GET  /count   JSON {project, views, downloads, total} plus additive human/bot
 * GET  /stats   JSON totals + additive human/bot + per-repo + per-branch
 * POST /event   forks report a download {owner,repo,branch,fork,asset}
 * /v1, /mcp, and /v1/mesh/* do not increment views or downloads.
 *
 * KV binding DOWNLOADS. Keys: project|owner|repo|branch|fork
 * totalKey() = ark|__total__
 * Additive split keys (fleet copy): ark|__views_human__ / __views_bot__ /
 * __downloads_human__ / __downloads_bot__. Legacy totals are never reset.
 * /stats derives the bot bucket so views === views_human + views_bot.
 * CORS *. No secrets in this tree.
 * Isolated counter: Worker ark-download-tracker, project ark.
 * Not mixed with any other product.
 *
 * Hosted /v1 never stores phrases or vault blobs.
 * Do NOT add unlock/encrypt/decrypt that takes a passphrase.
 */

const PROJECT = "ark";
const DEFAULT_ASSET = "ark-0.1.0.tar.gz";
const DEFAULT_OWNER = "AzielEliab";
const DEFAULT_REPO = "ark";
const DEFAULT_BRANCH = "main";
const HOST = "https://ark-download-tracker.vibelock.workers.dev";
const GITHUB_REPO = "https://github.com/AzielEliab/ark";

const GITHUB_RELEASES = "https://github.com/AzielEliab/ark/releases";
const GITHUB_LATEST = "https://github.com/AzielEliab/ark/releases/latest";
const INSTALL_LINE = "curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash";
const DOI = "https://doi.org/10.5281/zenodo.21435810";
const ZENODO = "https://zenodo.org/records/21435810";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, X-Aziel-Runtime-Token, User-Agent",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function redirect(url) {
  return new Response(null, {
    status: 302,
    headers: { Location: url, ...corsHeaders() },
  });
}

function splitOwnerRepo(value, fallbackOwner, fallbackRepo) {
  if (typeof value === "string" && value.includes("/")) {
    const [o, r] = value.split("/").filter(Boolean);
    if (o && r) return { owner: o, repo: r };
  }
  return { owner: fallbackOwner, repo: fallbackRepo };
}

function parseDims(src) {
  const get = (k) => {
    if (src == null) return null;
    if (typeof src.get === "function") {
      const v = src.get(k);
      return v == null || v === "" ? null : v;
    }
    const v = src[k];
    return v == null || v === "" ? null : v;
  };

  let owner = get("owner") || DEFAULT_OWNER;
  let repo = get("repo") || DEFAULT_REPO;
  if (typeof repo === "string" && repo.includes("/")) {
    const split = splitOwnerRepo(repo, owner, DEFAULT_REPO);
    owner = split.owner;
    repo = split.repo;
  }

  const branch = get("branch") || DEFAULT_BRANCH;
  const tag = get("tag") || "latest";
  const asset = get("asset") || "";

  const forkRaw = get("fork");
  let fork = "0";
  if (forkRaw === 1 || forkRaw === true || forkRaw === "1" || forkRaw === "true") {
    fork = "1";
  } else if (typeof forkRaw === "string" && forkRaw.includes("/")) {
    const split = splitOwnerRepo(forkRaw, owner, repo);
    owner = split.owner;
    repo = split.repo;
    fork = "1";
  } else if (forkRaw != null && forkRaw !== 0 && forkRaw !== false && forkRaw !== "0" && forkRaw !== "false") {
    fork = "1";
  }

  if (`${owner}/${repo}`.toLowerCase() !== `${DEFAULT_OWNER}/${DEFAULT_REPO}`.toLowerCase()) {
    fork = "1";
  }

  return { project: PROJECT, owner, repo, branch, fork, tag, asset };
}

function kvKey(dims) {
  return `${dims.project}|${dims.owner}|${dims.repo}|${dims.branch}|${dims.fork}`;
}

function githubAssetUrl(owner, repo, tag, asset) {
  if (!asset) {
    if (owner === DEFAULT_OWNER && repo === DEFAULT_REPO) return GITHUB_RELEASES;
    return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases`;
  }
  if (!tag || tag === "latest") {
    return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases/latest/download/${encodeURIComponent(asset)}`;
  }
  return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases/download/${encodeURIComponent(tag)}/${encodeURIComponent(asset)}`;
}

function totalKey() {
  return splitKeys(PROJECT).downloads;
}

async function incrementClassified(env, request, kind) {
  const keys = splitKeys(PROJECT);
  const cls = classifyRequest(request);
  const humanKey = kind === "views" ? keys.viewsHuman : keys.downloadsHuman;
  const botKey = kind === "views" ? keys.viewsBot : keys.downloadsBot;
  await incrementSplitKey(env, cls.kind === "human" ? humanKey : botKey);
  return cls;
}

async function increment(env, dims, request) {
  const key = kvKey(dims);
  const n = parseInt((await env.DOWNLOADS.get(key)) || "0", 10) + 1;
  await env.DOWNLOADS.put(key, String(n));
  const tot = parseInt((await env.DOWNLOADS.get(totalKey())) || "0", 10) + 1;
  await env.DOWNLOADS.put(totalKey(), String(tot));
  if (request) await incrementClassified(env, request, "downloads");
  return tot;
}

async function listAllKeys(env) {
  const keys = [];
  let cursor;
  do {
    const page = await env.DOWNLOADS.list(cursor ? { cursor } : {});
    keys.push(...page.keys);
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  return keys;
}

async function collectStats(env, request) {
  const keys = await listAllKeys(env);
  let total = 0;
  const by_repo = {};
  const by_branch = {};
  const by_fork = { "0": 0, "1": 0 };
  const breakdown = [];

  for (const k of keys) {
    const name = k.name;
    if (isStatsMetaKey(name, PROJECT)) continue;
    const n = parseInt((await env.DOWNLOADS.get(name)) || "0", 10);
    if (!Number.isFinite(n) || n <= 0) continue;
    const parts = name.split("|");
    if (parts.length < 5) continue;
    const [project, owner, repo, branch, fork] = parts;
    total += n;
    const repoId = `${owner}/${repo}`;
    by_repo[repoId] = (by_repo[repoId] || 0) + n;
    by_branch[branch] = (by_branch[branch] || 0) + n;
    const forkFlag = fork === "1" ? "1" : "0";
    by_fork[forkFlag] = (by_fork[forkFlag] || 0) + n;
    breakdown.push({ project, owner, repo, branch, fork: forkFlag, count: n });
  }

  const totalDirect = parseInt((await env.DOWNLOADS.get(totalKey())) || "0", 10);
  const shown = Number.isFinite(totalDirect) && totalDirect > 0 ? totalDirect : total;
  const split = await readSplitCounters(env, PROJECT);
  const views = split.views;
  return shapeStats(
    {
      project: PROJECT,
      views,
      downloads: shown,
      total: shown,
      views_human: split.views_human,
      views_bot: split.views_bot,
      downloads_human: split.downloads_human,
      downloads_bot: split.downloads_bot,
      classification: classificationBlock(request),
    },
    {
      by_repo,
      by_branch,
      by_fork,
      breakdown,
      github: (await githubStats(env)),
      note: "Forks identified by GitHub owner/repo. Key layout: project|owner|repo|branch|fork. Additive human/bot: derive bot on read (legacy totals not reset).",
    },
  );
}



function viewsKey() {
  return splitKeys(PROJECT).views;
}

function githubCacheKey() {
  return splitKeys(PROJECT).github;
}

async function incrementViews(env, request) {
  const n = parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) + 1;
  await env.DOWNLOADS.put(viewsKey(), String(n));
  if (request) await incrementClassified(env, request, "views");
  return n;
}

async function githubStats(env) {
  const cached = await env.DOWNLOADS.get(githubCacheKey());
  if (cached) {
    try {
      const obj = JSON.parse(cached);
      if (obj && obj.fetched_at && Date.now() - obj.fetched_at < 5 * 60 * 1000) {
        return obj;
      }
    } catch {
      /* ignore */
    }
  }
  const headers = { "User-Agent": "Mozilla/5.0 The ARK-download-tracker", Accept: "application/vnd.github+json" };
  let stars = 0;
  let forks = 0;
  let watchers = 0;
  let release_download_count = 0;
  try {
    const repoRes = await fetch("https://api.github.com/repos/AzielEliab/ark", { headers });
    if (repoRes.ok) {
      const repo = await repoRes.json();
      stars = Number(repo.stargazers_count) || 0;
      forks = Number(repo.forks_count) || 0;
      watchers = Number(repo.subscribers_count != null ? repo.subscribers_count : repo.watchers_count) || 0;
    }
    const relRes = await fetch("https://api.github.com/repos/AzielEliab/ark/releases/latest", { headers });
    if (relRes.ok) {
      const rel = await relRes.json();
      const assets = Array.isArray(rel.assets) ? rel.assets : [];
      release_download_count = assets.reduce((s, a) => s + (Number(a.download_count) || 0), 0);
    }
  } catch {
    /* public API; empty is fine */
  }
  const out = { stars, forks, watchers, release_download_count, fetched_at: Date.now() };
  try {
    await env.DOWNLOADS.put(githubCacheKey(), JSON.stringify(out));
  } catch {
    /* ignore */
  }
  return out;
}

function installScript() {
  return `#!/usr/bin/env bash\n# The ARK one-click install. Counted download via this Worker.\nset -euo pipefail\nHOST="${HOST}"\nASSET="${DEFAULT_ASSET}"\nWORKDIR="\${ARK_HOME:-\$HOME/ark}"\nmkdir -p "\$WORKDIR"\ncd "\$WORKDIR"\necho "Downloading counted tarball from \${HOST}/download (User-Agent Mozilla/5.0)…"\ncurl -fsSL -A 'Mozilla/5.0' "\${HOST}/download?asset=\${ASSET}" -o "\${ASSET}"\ntar -xzf "\${ASSET}"\nDIR=\"\$(find . -maxdepth 1 -type d -name 'ark-*' | head -n 1)\"\nif [ -n "\${DIR}" ]; then\n  cd "\${DIR}"\nfi\npython3 -m venv .venv\n. .venv/bin/activate\npython -m pip install -U pip\npython -m pip install -e .\necho\necho "Installed The ARK."\necho "Run:  ark ui"\necho "Then open http://127.0.0.1:8850  (loopback only)"\necho "Author: Aziel Eliab."\n`;
}

async function serveAsset(request, env, asset, { head = false } = {}) {
  if (!env.ASSETS) {
    return json({ error: "assets binding missing" }, 500);
  }
  const assetUrl = new URL("/" + asset, request.url);
  const assetRes = await env.ASSETS.fetch(new Request(assetUrl, { method: "GET" }));
  if (!assetRes.ok) {
    return json({ error: "asset not hosted", asset, status: assetRes.status }, 404);
  }
  const headers = new Headers();
  headers.set("Content-Type", "application/gzip");
  headers.set("Content-Disposition", 'attachment; filename="' + asset.replaceAll('"', "") + '"');
  headers.set("Cache-Control", "private, no-store");
  const len = assetRes.headers.get("Content-Length");
  if (len) headers.set("Content-Length", len);
  for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
  if (head) {
    return new Response(null, { status: 200, headers });
  }
  return new Response(assetRes.body, { status: 200, headers });
}

async function indexHtml(env) {
  const stats = await collectStats(env);
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const views = parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const breakdown = (stats.breakdown || [])
    .map(
      (b) =>
        `<li><code>${b.owner}/${b.repo}</code> branch <code>${b.branch}</code> fork=${b.fork} → ${b.count}</li>`,
    )
    .join("") || "<li>none yet</li>";
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The ARK — Aziel Eliab</title>
<meta name="description" content="Local deniable vault by Aziel Eliab: every phrase is a login, and an empty vault is indistinguishable from a wrong phrase.">
<meta name="author" content="Aziel Eliab">
<link rel="canonical" href="https://ark-download-tracker.vibelock.workers.dev/">
<link rel="icon" href="/sigil.png" type="image/png">
<meta property="og:title" content="The ARK — Aziel Eliab">
<meta property="og:description" content="Local deniable vault by Aziel Eliab: every phrase is a login, and an empty vault is indistinguishable from a wrong phrase.">
<meta property="og:url" content="https://ark-download-tracker.vibelock.workers.dev/">
<meta property="og:image" content="https://ark-download-tracker.vibelock.workers.dev/sigil.png">
<meta property="og:image:alt" content="Aziel Eliab rose-star brand mark. Author Aziel Eliab.">
<meta name="twitter:image" content="https://ark-download-tracker.vibelock.workers.dev/sigil.png">
<meta name="twitter:image:alt" content="Aziel Eliab rose-star brand mark. Author Aziel Eliab.">
<meta property="og:type" content="website">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "The ARK",
  "author": {
    "@type": "Person",
    "name": "Aziel Eliab"
  },
  "codeRepository": "https://github.com/AzielEliab/ark",
  "downloadUrl": "https://ark-download-tracker.vibelock.workers.dev/download",
  "license": "https://www.apache.org/licenses/LICENSE-2.0",
  "url": "https://ark-download-tracker.vibelock.workers.dev/",
  "description": "Local deniable vault by Aziel Eliab: every phrase is a login, and an empty vault is indistinguishable from a wrong phrase.",
  "identifier": "https://doi.org/10.5281/zenodo.21435810"
}
</script>
<!-- gitbaby-seo -->
<style>
  :root {
    color-scheme: dark;
    --bg: #0c0d10;
    --ink: #f4f1ea;
    --muted: #c9c2b4;
    --panel: #16181d;
    --line: #3a3428;
    --gold: #e6c35c;
    --btn-bg: #f4f1ea;
    --btn-ink: #14120c;
    --focus: #ffe08a;
    --link: #f0d78c;
    --pass: #146c43;
  }
  @media (prefers-color-scheme: light) {
    :root {
      color-scheme: light;
      --bg: #f7f5f1;
      --ink: #1c1915;
      --muted: #3f3a33;
      --panel: #ffffff;
      --line: #d9d2c4;
      --gold: #5c4300;
      --btn-bg: #1c1915;
      --btn-ink: #f7f5f1;
      --focus: #0842a0;
      --link: #5c4300;
      --pass: #0e6b3c;
    }
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; background: var(--bg); color: var(--ink); }
  body {
    font: 16px/1.5 system-ui, "Segoe UI", sans-serif;
    overflow-x: clip;
  }
  a { color: var(--link); }
  code, pre { font-family: ui-monospace, Menlo, Consolas, monospace; }
  code { font-size: .92em; }
  .hero, main, footer.quiet {
    width: min(40rem, 100%);
    margin: 0 auto;
    padding-left: 1.15rem;
    padding-right: 1.15rem;
  }
  .hero { padding-top: 1.35rem; }
  .brandrow { display: flex; align-items: center; justify-content: flex-start; gap: 12px; margin: 0 0 .85rem; }
  .brandmark { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 auto; box-shadow: 0 0 0 1px #d4af3733; }
  h1 { font-size: 2rem; font-weight: 650; letter-spacing: .02em; margin: 0 0 .25rem; line-height: 1.15; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 .55rem; font-size: 1.08rem; }
  .lede, .honesty, .kid, .asset-note { color: var(--muted); margin: 0 0 .9rem; max-width: 38rem; }
  .asset-note { font-size: .92rem; }
  .honesty { font-size: .92rem; }
  a.btn.block.primary {
    display: block;
    width: 100%;
    max-width: 36rem;
    margin: .15rem 0 .7rem;
    padding: 1.05rem 1.2rem;
    border: 2px solid transparent;
    border-radius: 12px;
    background: var(--btn-bg);
    color: var(--btn-ink);
    text-align: center;
    text-decoration: none;
    font: 750 1.25rem/1.1 ui-monospace, Menlo, Consolas, monospace;
    letter-spacing: .02em;
    cursor: pointer;
  }
  a.btn.block.primary:hover { filter: brightness(1.06); }
  .features {
    list-style: none;
    margin: .15rem 0 1rem;
    padding: 0;
    display: grid;
    gap: .45rem;
    max-width: 38rem;
  }
  .features li { margin: 0; padding-left: 1.05rem; position: relative; }
  .features li::before {
    content: "";
    width: .45rem;
    height: .45rem;
    border-radius: 50%;
    background: var(--gold);
    position: absolute;
    left: 0;
    top: .5rem;
  }
  .card, .cite {
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 1rem 1.05rem 1.1rem;
    background: var(--panel);
    margin: 0 0 1rem;
    max-width: 100%;
  }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 .85rem; }
  .count { font-size: 2rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; color: var(--ink); }
  .count span { display: block; font-size: .92rem; font-weight: 500; color: var(--muted); }
  button.btn.install {
    font: 700 .95rem/1.1 ui-monospace, Menlo, Consolas, monospace;
    padding: .72rem 1rem;
    border-radius: 9px;
    border: 1px solid var(--line);
    background: transparent;
    color: var(--ink);
    cursor: pointer;
  }
  button.btn.install.copied { background: var(--pass); color: #f4f1ea; border-color: transparent; }
  pre {
    background: var(--bg);
    color: var(--ink);
    padding: .75rem .9rem;
    border-radius: 8px;
    border: 1px solid var(--line);
    font-size: .82rem;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    max-width: 100%;
    margin: .75rem 0 0;
  }
  h2 { font-size: 1rem; margin: 0 0 .45rem; letter-spacing: .04em; }
  .meta, .iso { margin: .75rem 0 0; color: var(--muted); font-size: .9rem; }
  .cite h2 { font-size: 1.05rem; }
  .cite p { margin: .35rem 0; }
  ul { margin: .3rem 0 0; padding-left: 1.15rem; }
  li { overflow-wrap: anywhere; }
  #meshStrip {
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: .85rem 1rem;
    background: var(--panel);
    margin: 0 0 1rem;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: .7rem 1rem;
    font-size: .88rem;
    color: var(--muted);
    max-width: 100%;
    min-width: 0;
  }
  #meshStrip .live { color: var(--ink); }
  #meshStrip .live b { color: var(--gold); font-size: 1.35rem; margin-right: .35rem; }
  #meshStrip .rollup b { color: var(--gold); }
  #meshStrip > span { display: flex; flex-wrap: wrap; gap: .45rem; max-width: 100%; min-width: 0; }
  #meshStrip button {
    font: 700 .78rem/1 ui-monospace, Menlo, Consolas, monospace;
    height: 2rem;
    padding: 0 .75rem;
    border-radius: 8px;
    background: transparent;
    color: var(--ink);
    border: 1px solid var(--line);
    cursor: pointer;
  }
  #meshStrip button:hover { border-color: var(--gold); color: var(--gold); }
  #meshStrip input {
    width: min(16rem, 100%);
    max-width: 100%;
    min-width: 0;
    padding: .4rem .55rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--bg);
    color: var(--ink);
    font: inherit;
  }
  #meshProducts { flex-basis: 100%; margin: 0; overflow-wrap: anywhere; min-width: 0; }
  a:focus-visible, button:focus-visible, input:focus-visible {
    outline: 3px solid var(--focus);
    outline-offset: 3px;
  }
  a.skip {
    position: absolute;
    left: 1rem;
    top: 0;
    transform: translateY(-140%);
    background: var(--btn-bg);
    color: var(--btn-ink);
    padding: .45rem .7rem;
    border-radius: 8px;
    text-decoration: none;
    z-index: 5;
  }
  a.skip:focus, a.skip:focus-visible { transform: none; }
  footer.quiet { padding-top: .35rem; padding-bottom: 2.6rem; color: var(--muted); font-size: .9rem; }
  footer.quiet p { margin: .35rem 0; }
  footer.quiet a { color: var(--ink); }
  @media (max-width: 520px) {
    .hero { padding-top: 1.1rem; }
    a.btn.block.primary { max-width: none; }
    h1 { font-size: 1.75rem; }
  }
</style>
<body>
  <a class="skip" href="#downloadBtn">Skip to download</a>
  <header class="hero">
    <div class="brandrow"><img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async"></div>
    <h1>The ARK</h1>
    <p class="motto">Local deniable vault. Every phrase opens its own vault.</p>
    <p class="lede">The phrase stays on this computer. AES-256-GCM, Argon2id, and HKDF. After install, run <code>ark ui</code> and open http://127.0.0.1:8850.</p>
    <a class="btn block primary" id="downloadBtn" href="/download?asset=${DEFAULT_ASSET}">Download</a>
    <p class="asset-note" id="downloadNote">${n} downloads · ${DEFAULT_ASSET} · counted on this Worker for every branch and fork</p>
    <ul class="features">
      <li>One phrase opens one vault on this computer</li>
      <li>An empty vault looks the same as a wrong phrase</li>
      <li>A file is checked, then encrypted, before it is stored</li>
    </ul>
    <p class="honesty">A forgotten phrase cannot be recovered. This page counts downloads and never stores a phrase or a vault.</p>
  </header>
  <main>
    <section class="card" id="counts" aria-label="Counts">
      <div class="nums">
        <p class="count">${v}<span>Views</span></p>
        <p class="count">${n}<span>Downloads</span></p>
      </div>
      <p class="kid">One-click install copies a Terminal command. When it finishes, run <code>ark ui</code>.</p>
      <button type="button" class="btn install" id="install-btn">One-click install</button>
      <pre id="install-cmd">curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash</pre>
    </section>
    <aside id="meshStrip" aria-label="Live Nodes">
      <span class="live"><b id="meshLiveCount">0</b> Live Nodes</span>
      <span id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.</span>
      <span class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></span>
      <span>No Node Gate · No auto-heal · Aziel Eliab only</span>
      <span>
        <input id="meshBearer" type="text" placeholder="bearer (required to enable)" autocomplete="off" spellcheck="false" aria-label="Mesh bearer">
        <button type="button" id="meshEnable">Enable</button>
        <button type="button" id="meshDisable">Disable</button>
        <button type="button" id="meshJoin">Join</button>
        <button type="button" id="meshLeave">Leave</button>
      </span>
      <p id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cite · not AnonBroadcast · not AZMail ring · not a Node Gate · no public qnsd proxy</p>
    </aside>
    <section class="card" id="breakdown">
      <h2>Per repo / branch / fork</h2>
      <ul>${breakdown}</ul>
      <p class="meta">The download count ticks on the Download click. The Worker serves the gzip (HTTP 200). Forks using this same link are counted automatically. ${DEFAULT_ASSET} — ${n} counted.</p>
      <p class="iso">Isolated counter: Worker <code>ark-download-tracker</code>, project <code>ark</code>, KV <code>ARK_DOWNLOADS</code>. Not mixed with any other product. /v1, /mcp, and /v1/mesh/* do not increment downloads.</p>
    </section>
    <section class="cite" id="cite">
      <h2>How to cite</h2>
      <p>Aziel Eliab. The ARK. https://github.com/AzielEliab/ark. https://ark-download-tracker.vibelock.workers.dev. https://doi.org/10.5281/zenodo.21435810.</p>
    </section>
  </main>
  <footer class="quiet">
    <p>Apache-2.0 · Aziel Eliab · The ARK</p>
    <p><a href="${GITHUB_REPO}">GitHub</a> · <a href="https://aziel-runtime.vibelock.workers.dev/">Catalog</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/mcp">MCP</a> · <a href="/v1/mesh">Mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/ai">AI runtime</a> · <a href="/stats">Stats</a> · <a href="/count">Count</a> · <a href="/cite.json">Cite</a> · <a href="${DOI}">DOI</a> · <a href="${ZENODO}">Zenodo</a> · <a href="${GITHUB_LATEST}">Releases</a></p>
  </footer>

    <script>
      (function () {
        var cmd = "curl -fsSL https://ark-download-tracker.vibelock.workers.dev/install.sh | bash";
        var btn = document.getElementById("install-btn");
        var pre = document.getElementById("install-cmd");
        if (!btn) return;
        btn.addEventListener("click", function () {
          function done(ok) {
            btn.textContent = ok ? "Copied! Paste in Terminal, then run ark ui" : "Select the command, copy it, then run ark ui";
            btn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(cmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (pre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(pre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      })();
      (function () {
        function $(id) { return document.getElementById(id); }
        function meshNum() {
          for (var i = 0; i < arguments.length; i++) {
            var raw = arguments[i];
            if (raw == null || raw === "") continue;
            var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
            if (Number.isFinite(n) && n >= 0) return Math.floor(n);
          }
          return 0;
        }
        function unwrapMesh(j) {
          if (!j || typeof j !== "object") return {};
          if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
          if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
          return j;
        }
        function paintMesh(raw) {
          var j = unwrapMesh(raw);
          var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
          var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
          var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
          var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
          var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
          if ($("meshLiveCount")) $("meshLiveCount").textContent = String(live);
          if ($("qnmLive")) $("qnmLive").textContent = String(live);
          if ($("qnmLocked")) $("qnmLocked").textContent = String(locked);
          if ($("qnmIsolated")) $("qnmIsolated").textContent = String(isolated);
          var line = $("meshLine");
          if (line) {
            if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". QNS-CD-1.0. Not an anonymity network.";
            else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
            else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
          }
          var products = j.products_present || j.products || [];
          var names = Array.isArray(products) ? products.map(function (p) { return typeof p === "string" ? p : (p && (p.product || p.slug)) || ""; }).filter(Boolean) : [];
          var nodes = Array.isArray(j.nodes) ? j.nodes : [];
          var extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
          if ($("meshProducts")) $("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cite · not AnonBroadcast · not AZMail ring · not a Node Gate · no public qnsd proxy" + extra;
        }
        async function meshGet(path) {
          var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
          return r.json();
        }
        async function meshPost(path, payload) {
          var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
          return r.json();
        }
        async function refreshMesh() {
          try {
            var status = await meshGet("/v1/mesh");
            var merged = status;
            var inner = unwrapMesh(status);
            var on = inner.enabled === true;
            if (on) {
              try {
                var nodes = await meshGet("/v1/mesh/nodes");
                merged = Object.assign({}, inner, unwrapMesh(nodes));
              } catch (e) { /* status is enough */ }
            }
            paintMesh(merged);
            var nodeId = sessionStorage.getItem("ark_mesh_node");
            if (on && nodeId) {
              try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
            }
          } catch (e) {
            paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
          }
        }
        if ($("meshEnable")) $("meshEnable").onclick = async function () {
          var bearer = ($("meshBearer") && $("meshBearer").value || "").trim();
          paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
          refreshMesh();
        };
        if ($("meshDisable")) $("meshDisable").onclick = async function () {
          sessionStorage.removeItem("ark_mesh_node");
          paintMesh(await meshPost("/v1/mesh/disable", {}));
          refreshMesh();
        };
        if ($("meshJoin")) $("meshJoin").onclick = async function () {
          var j = await meshPost("/v1/mesh/join", { product: "ark", label: "The ARK Worker" });
          var inner = unwrapMesh(j);
          var id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
          if (id) sessionStorage.setItem("ark_mesh_node", String(id));
          paintMesh(j);
          refreshMesh();
        };
        if ($("meshLeave")) $("meshLeave").onclick = async function () {
          var id = sessionStorage.getItem("ark_mesh_node");
          if (id) await meshPost("/v1/mesh/leave", { node_id: id });
          sessionStorage.removeItem("ark_mesh_node");
          refreshMesh();
        };
        window.addEventListener("pagehide", function () {
          var id = sessionStorage.getItem("ark_mesh_node");
          if (!id || typeof navigator.sendBeacon !== "function") return;
          try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
        });
        refreshMesh();
        setInterval(refreshMesh, 30000);
        document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshMesh(); });
      })();
    </script>
<!-- /gitbaby-seo -->
</body>
</html>`;
}


function html(body) {
  return new Response(body, {
    headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return "https://ark-download-tracker.vibelock.workers.dev";
  }
}

function openapiSpec(request) {
  const origin = originOf(request);
  return {
    openapi: "3.1.0",
    info: {
      title: "The ARK runtime",
      version: "0.1.0",
      summary: "Local deniable vault. Hosted API is heuristics only. Not a kernel.",
      description: engine.LIMITATION + " Suite mesh /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Aziel Eliab only.",
    },
    servers: [{ url: origin }],
    paths: {
            "/v1/example": { get: { operationId: "arkExample", summary: "Sample JSON payload. Does not increment downloads.", responses: { "200": { description: "OK" } } } },
      "/v1/health": { get: { operationId: "ark_health", summary: "Liveness. Does not increment download KV. Never stores phrases.", responses: { "200": { description: "ok" } } } },
      "/v1/levels": { get: { operationId: "ark_levels", summary: "Auto-lock seconds and decoy counts. Behavior, not cryptography.", responses: { "200": { description: "levels" } } } },
      ...meshOpenApiPaths(),
      "/v1/sweep": {
        post: {
          operationId: "ark_sweep",
          summary: "Mode E heuristics only (PE/ELF/Mach-O, powershell -enc, curl|sh). No clamscan. Payload is not stored.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { b64: { type: "string" }, text: { type: "string" } } } } } },
          responses: { "200": { description: "findings" } },
        },
      },
    },
  };
}

function aiHelpPage(request) {
  const origin = originOf(request);
  return `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The ARK — AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 44rem; margin: 3rem auto; padding: 0 1.25rem; background: #0e1014; color: #e8eaef; }
  .brandrow { display: flex; align-items: center; justify-content: flex-start; gap: 12px; margin: 0 0 1.15rem; }
  .brandmark { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 auto; box-shadow: 0 0 0 1px #d4af3733; }
  a { color: #c9d4ff; }
  code, pre { background: #151922; padding: .15rem .35rem; border-radius: 4px; }
  pre { padding: .85rem 1rem; overflow: auto; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; }
</style>
<body>
<div class="brandrow"><img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async"></div>
<h1>The ARK runtime</h1>
<p class="banner">${engine.LIMITATION}</p>
<h2>Use with AI assistants</h2>
<p>Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants.</p>
<p>Import the catalog or Worker OpenAPI as a custom tool (Grok, Claude, Gemini, and similar), as a GPT Action in ChatGPT (no auth), or as HTTP tools (Venice and other HTTP-tool clients). Cursor and Glama: connect the catalog MCP. Always send <code>User-Agent: Mozilla/5.0</code>.</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>Catalog: <a href="https://aziel-runtime.vibelock.workers.dev/">aziel-runtime.vibelock.workers.dev</a></p>
<pre>curl ${origin}/v1/health
curl ${origin}/v1/levels
curl -X POST ${origin}/v1/sweep -H 'content-type: application/json' \\
  -d '{"text":"hello"}'
</pre>
<p>Suite mesh: GET <a href="${origin}/v1/mesh">${origin}/v1/mesh</a> PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer (hub cite / Worker mesh cross-map only; no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity. Catalog MCP mesh_* + FragGate slug=mesh. Author: Aziel Eliab only.</p>
<p>GET/POST under <code>/v1</code> never increment the download counter. Sweep does not store the payload. There is no cloud unlock.</p>
<p><a href="/">Downloads</a></p>
</body></html>`;
}

export async function handleRuntime(request, url, env) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (isMeshPath(path) || path === "/v1/mesh") {
    const out = await runMeshProxy(env, request, path + (url.search || ""));
    if (request.method === "HEAD") {
      return new Response(null, { status: out.status, headers: corsHeaders() });
    }
    return json(out.data, out.status);
  }
  if (path === "/v1/health" && request.method === "GET") {
    return json({
      ok: true, author: "Aziel Eliab",
      identity: "Aziel Eliab",
      product: "ark",
      runtime: true,
      kv_increment: false,
      stores_phrases: false,
      stores_vaults: false,
      not_a_kernel: true,
      mesh: meshPointer(),
      limitation: engine.LIMITATION,
    });
  }
  if ((path === "/v1/example" || path === "/v1/example/") && (request.method === "GET" || request.method === "HEAD")) {
    return json({
      ok: true,
      product: "ark",
      author: "Aziel Eliab",
      example: EXAMPLE_PAYLOAD,
      note: "Sample payload only. Does not increment downloads.",
    });
  }


  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL_MARKDOWN, {
      status: 200,
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Cache-Control": "private, no-store",
        "X-KV-Increment": "false",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  if (path === "/v1/levels" && request.method === "GET") {
    return json(engine.levels());
  }
  if ((path === "/mcp" || path === "/mcp/") && (request.method === "GET" || request.method === "HEAD")) {
    const body = {
      ok: true,
      product: "ark",
      author: "Aziel Eliab",
      identity: "Aziel Eliab",
      catalog_mcp: "https://aziel-runtime.vibelock.workers.dev/mcp",
      catalog_openapi: "https://aziel-runtime.vibelock.workers.dev/openapi.json",
      worker_openapi: originOf(request) + "/openapi.json",
      fraggate_slug: "ark",
      mesh: meshPointer(),
      mesh_body: { slug: "mesh", op: "status", payload: {} },
      kv_increment: false,
      note: "Dual surface: human Worker UI and this MCP pointer. Canonical agent path is the catalog MCP on aziel-runtime (FragGate slug ark). Catalog MCP mesh_* + FragGate slug=mesh. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM rollup live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer (hub cite / Worker mesh cross-map only; no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity.",
    };
    if (request.method === "HEAD") return new Response(null, { status: 200, headers: corsHeaders() });
    return json(body);
  }
  if (path === "/openapi.json" && request.method === "GET") {
    return json(openapiSpec(request));
  }
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return html(aiHelpPage(request));
  }
  if (path === "/v1/sweep" && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required", limitation: engine.LIMITATION }, 400);
    }
    return json(engine.sweep(body || {}));
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health /v1/levels GET /v1/mesh ; POST /v1/sweep", mesh: meshPointer(), limitation: engine.LIMITATION }, 404);
  }
  return null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const runtime = await handleRuntime(request, url, env);
    if (runtime) return runtime;

    if ((url.pathname === "/install.sh" || url.pathname === "/install.sh/") && request.method === "GET") {
      return new Response(installScript(), {
        status: 200,
        headers: {
          "Content-Type": "text/x-shellscript; charset=utf-8",
          "Cache-Control": "private, no-store",
          ...corsHeaders(),
        },
      });
    }

    if (url.pathname === "/" && request.method === "GET") {
      await incrementViews(env, request);
      return new Response(await indexHtml(env), {
        headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
      });
    }

    if (url.pathname === "/count" && request.method === "GET") {
      const stats = await collectStats(env, request);
      return json(shapeCount(stats));
    }

    if (url.pathname === "/stats" && request.method === "GET") {
      return json(await collectStats(env, request));
    }

    if (url.pathname === "/event" && request.method === "POST") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "JSON body required" }, 400);
      }
      const dims = parseDims(body || {});
      const count = await increment(env, dims, request);
      return json({
        ok: true,
        key: kvKey(dims),
        count,
        owner: dims.owner,
        repo: dims.repo,
        branch: dims.branch,
        fork: dims.fork,
        asset: dims.asset || null,
      });
    }

    if (url.pathname === "/go" && (request.method === "GET" || request.method === "HEAD")) {
      const dims = parseDims(url.searchParams);
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      if (request.method === "GET") await increment(env, dims, request);
      return serveAsset(request, env, asset, { head: request.method === "HEAD" });
    }

    if ((url.pathname === "/download" || url.pathname.startsWith("/download/")) && (request.method === "GET" || request.method === "HEAD")) {
      const dims = parseDims(url.searchParams);
      if (!dims.asset && url.pathname.startsWith("/download/")) {
        dims.asset = decodeURIComponent(url.pathname.slice("/download/".length));
      }
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      if (request.method === "GET") await increment(env, dims, request);
      return serveAsset(request, env, asset, { head: request.method === "HEAD" });
    }


    // gitbaby-seo-routes
    if ((url.pathname === "/robots.txt" || url.pathname === "/robots.txt/") && request.method === "GET") {
      const body = "User-agent: *\nAllow: /\nSitemap: " + HOST + "/sitemap.xml\n";
      return new Response(body, {
        status: 200,
        headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() },
      });
    }
    if ((url.pathname === "/sitemap.xml" || url.pathname === "/sitemap.xml/") && request.method === "GET") {
      const locs = [HOST + "/", HOST + "/download", HOST + "/install.sh", HOST + "/v1/skill", HOST + "/v1/mesh", HOST + "/openapi.json", HOST + "/mcp", GITHUB_REPO];
      const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + locs.map((u) => "  <url><loc>" + u + "</loc></url>").join("\n")
        + "\n</urlset>\n";
      return new Response(xml, {
        status: 200,
        headers: { "Content-Type": "application/xml; charset=utf-8", ...corsHeaders() },
      });
    }
    if ((url.pathname === "/cite.json" || url.pathname === "/cite.json/") && request.method === "GET") {
      return json({"author": "Aziel Eliab", "identity": "Aziel Eliab only", "title": "The ARK", "github": "https://github.com/AzielEliab/ark", "download": "https://ark-download-tracker.vibelock.workers.dev/download", "doi": "10.5281/zenodo.21435810", "license": "Apache-2.0", "catalog": "https://aziel-runtime.vibelock.workers.dev/", "mesh": HOST + "/v1/mesh", "mesh_catalog": "https://aziel-runtime.vibelock.workers.dev/v1/mesh"});
    }
    // /gitbaby-seo-routes
    return json({ error: "not found" }, 404);
  },
};
