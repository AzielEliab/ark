"""Suite mesh Live Nodes + QNM-BUILD-1.0 contract.

Default OFF. live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = (ROOT / "workers/download-tracker/src/mesh.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
WRANGLER = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
WORKER_README = (ROOT / "workers/download-tracker/README.md").read_text(encoding="utf-8")


def test_mesh_contract_default_off_qnm_law() -> None:
    assert 'QNM_SPEC = "QNM-BUILD-1.0"' in MESH
    assert "MESH_DEFAULT_OFF = true" in MESH
    assert "MESH_ANONYMITY_NETWORK = false" in MESH
    assert "MESH_NODE_GATE = false" in MESH
    assert "MESH_AUTO_HEAL = false" in MESH
    assert "MESH_IDENTITY = IDENTITY" in MESH or '"Aziel Eliab"' in MESH
    assert 'MESH_PRODUCT = "ark"' in MESH
    assert 'MESH_PATH = "/v1/mesh"' in MESH
    assert "live|locked|isolated" in MESH
    assert "enabled_default: false" in MESH
    assert "anon_broadcast_publish_path: false" in MESH
    assert 'QNS_CD_SPEC = "QNS-CD-1.0"' in MESH
    assert "export const QNS_CD" in MESH
    assert "photon QNS1 packet transfer" in MESH
    assert "QNS-CD-1.0" in MESH
    assert "No public qnsd proxy" in MESH or "no public qnsd proxy" in MESH
    assert "Aziel Eliab" in MESH


def test_mesh_pointer_and_openapi_helpers() -> None:
    assert "export function meshPointer" in MESH
    assert "export function meshOpenApiPaths" in MESH
    assert "export function parseMeshDoc" in MESH
    assert "export function emptyMesh" in MESH
    assert "export function alignLiveNodes" in MESH
    assert "fraggate_slug: MESH_SLUG" in MESH
    assert "ark_mesh_" in MESH


def test_mesh_js_proxies_via_aziel_runtime() -> None:
    assert "MESH_ROUTE_METHODS" in MESH
    assert "isMeshPath" in MESH
    assert "runMeshProxy" in MESH
    assert "originFetch" in MESH
    assert "joinOriginUrl" in MESH
    assert '"/v1/mesh"' in MESH
    assert 'startsWith("/v1/mesh/")' in MESH
    assert "AZIEL_RUNTIME" in WRANGLER
    assert "aziel-runtime" in WRANGLER
    assert "/v1/mesh" in WRANGLER
    assert "c7305a73417348f6ad41a3529f0d0235" in WRANGLER


def test_index_advertises_mesh_proxy_and_pointer() -> None:
    assert 'from "./mesh.js"' in INDEX
    assert "meshPointer" in INDEX
    assert "meshOpenApiPaths" in INDEX
    assert "...meshOpenApiPaths()" in INDEX
    assert "mesh: meshPointer()" in INDEX
    assert "/v1/mesh" in INDEX
    assert "QNM-BUILD-1.0" in INDEX
    assert "No Node Gate" in INDEX
    assert "runMeshProxy" in INDEX
    assert "isMeshPath" in INDEX
    assert "handleRuntime(request, url, env)" in INDEX


def test_home_live_nodes_strip_no_node_gate() -> None:
    assert 'id="meshStrip"' in INDEX
    assert 'id="meshLiveCount"' in INDEX
    assert 'id="meshLine"' in INDEX
    assert "Live Nodes" in INDEX
    assert "QNM-BUILD-1.0" in INDEX
    assert "No Node Gate" in INDEX
    assert "No auto-heal" in INDEX
    assert "Not an anonymity network" in INDEX
    assert "/v1/mesh" in INDEX
    assert 'product: "ark"' in INDEX
    assert 'id="node-gate"' not in INDEX
    assert 'href="/node-gate"' not in INDEX
    assert "auto-heal this node" not in INDEX


def test_mcp_and_openapi_point_at_suite_mesh() -> None:
    assert "meshPointer" in INDEX
    assert "meshOpenApiPaths" in INDEX
    assert "/v1/mesh" in INDEX
    assert "QNM-BUILD-1.0" in INDEX
    assert "No Node Gate" in INDEX
    assert "mesh_*" in INDEX or "mesh_\\*" in INDEX
    assert "enabled_default=false" in INDEX or "enabled_default: false" in MESH


def test_docs_advertise_mesh_proxy() -> None:
    assert "/v1/mesh" in README
    assert "/v1/mesh" in SKILL
    assert "QNM-BUILD-1.0" in WORKER_README
    assert "QNS-CD-1.0" in README
    assert "QNS-CD-1.0" in SKILL
    assert "QNS-CD-1.0" in WORKER_README
    assert "AZIEL_RUNTIME" in WORKER_README
    assert "Live Nodes" in WORKER_README
    assert "Aziel Eliab" in MESH


def test_home_rose_star_brandmark_no_everblooming_on_mark() -> None:
    """Worker UI chrome: rose-star top-left, empty alt, no words on the mark."""
    mark = (
        '<div class="brandrow"><img class="brandmark" src="/sigil.png" '
        'width="40" height="40" alt="" decoding="async"></div>'
    )
    assert mark in INDEX
    assert ".brandrow" in INDEX
    assert ".brandmark" in INDEX
    assert 'src="/sigil.png"' in INDEX
    assert 'alt=""' in INDEX
    assert 'alt="Everblooming sigil' not in INDEX
    assert 'alt="everblooming sigil' not in INDEX
    assert "Everblooming sigil ·" not in INDEX
    # Scrub is for the public mark only. Do not rewrite header/skill strings
    # if a verify contract later requires the words "Everblooming".
    brand_start = INDEX.find('<div class="brandrow">')
    brand_end = INDEX.find("</div>", brand_start) + len("</div>")
    brand = INDEX[brand_start:brand_end]
    assert "everblooming" not in brand.lower()
    assert 'alt=""' in brand
    assert "MESH_DEFAULT_OFF = true" in MESH


def test_public_sigil_png_is_rose_star_asset() -> None:
    sigil = ROOT / "workers/download-tracker/public/sigil.png"
    data = sigil.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(data) > 1024


def test_qns_cd_cross_map_not_a_product() -> None:
    assert "softwares_tab: false" in MESH
    assert "public_proxy: false" in MESH
    assert "qnsd: false" in MESH
    assert "https://github.com/AzielEliab/qnm-node" in MESH
    assert "https://github.com/AzielEliab/aziel-runtime" in MESH
    assert "https://github.com/AzielEliab/azinterface" in MESH
    assert "attachQnsCd" in MESH
    assert "QNS-CD-1.0" in INDEX
    assert "no public qnsd proxy" in INDEX
