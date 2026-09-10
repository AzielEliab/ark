/**
 * Offline suite mesh PROXY check.
 * GET /v1/mesh/status is MESH-OK style with enabled:false.
 * Enable without bearer stays OFF (MESH-NEED-BEARER).
 * Author: Aziel Eliab. Apache-2.0.
 */
import assert from "node:assert/strict";
import {
  attachQnsCd,
  joinOriginUrl,
  meshPointer,
  QNS_CD,
  QNS_CD_SPEC,
  MESH_NOTE,
  runMeshProxy,
  SERVICE_BINDING_ORIGIN,
  DEFAULT_RUNTIME_ORIGIN,
} from "../src/mesh.js";
import { handleRuntime } from "../src/index.js";

const HOST = "https://ark-download-tracker.vibelock.workers.dev";

assert.equal(joinOriginUrl(DEFAULT_RUNTIME_ORIGIN, "/v1/mesh"), `${DEFAULT_RUNTIME_ORIGIN}/v1/mesh`);
assert.equal(joinOriginUrl(DEFAULT_RUNTIME_ORIGIN, "/v1/mesh/nodes"), `${DEFAULT_RUNTIME_ORIGIN}/v1/mesh/nodes`);
assert.equal(joinOriginUrl(DEFAULT_RUNTIME_ORIGIN, "/v1/mesh/status"), `${DEFAULT_RUNTIME_ORIGIN}/v1/mesh/status`);
assert.equal(meshPointer().enabled_default, false);
assert.equal(meshPointer().node_gate, false);
assert.equal(meshPointer().rollup, "live|locked|isolated");
assert.equal(meshPointer().fraggate_slug, "mesh");
assert.equal(QNS_CD_SPEC, "QNS-CD-1.0");
assert.equal(QNS_CD.spec, "QNS-CD-1.0");
assert.equal(QNS_CD.packet, "QNS1");
assert.equal(QNS_CD.transfer, "photon");
assert.equal(QNS_CD.public_proxy, false);
assert.equal(QNS_CD.qnsd, false);
assert.equal(QNS_CD.node_gate, false);
assert.equal(QNS_CD.softwares_tab, false);
assert.equal(QNS_CD.default_off, true);
assert.equal(meshPointer().qns_cd_spec, "QNS-CD-1.0");
assert.equal(meshPointer().qns_cd.spec, "QNS-CD-1.0");
assert.match(MESH_NOTE, /QNS-CD-1.0/);
assert.match(meshPointer().note, /QNS-CD-1.0/);
assert.equal(attachQnsCd({ ok: true }).qns_cd_spec, "QNS-CD-1.0");

const seen = [];
function jsonRes(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const env = {
  AZIEL_RUNTIME: {
    async fetch(request) {
      const url = new URL(request.url);
      seen.push({ method: request.method, href: request.url, path: url.pathname });
      if ((url.pathname === "/v1/mesh" || url.pathname === "/v1/mesh/status") && request.method === "GET") {
        return jsonRes({
          ok: true,
          code: "MESH-OK",
          enabled: false,
          radios: "off",
          mesh_default: "off",
          spec: "QNM-BUILD-1.0",
          rollup: { live: 0, locked: 0, isolated: 0 },
          live_nodes: 0,
          author: "Aziel Eliab",
        });
      }
      if (url.pathname === "/v1/mesh/enable" && request.method === "POST") {
        const body = await request.json();
        if (!body.bearer) return jsonRes({ ok: false, code: "MESH-NEED-BEARER", enabled: false }, 400);
        return jsonRes({ ok: true, code: "MESH-OK", enabled: true, radios: "on", bearers: [body.bearer] });
      }
      if (url.pathname === "/v1/mesh/join" && request.method === "POST") {
        return jsonRes({ ok: false, code: "MESH-OFF", enabled: false }, 409);
      }
      return jsonRes({ error: "not found", hint: "GET /v1/mesh GET /v1/mesh/status" }, 404);
    },
  },
};

const meshOp = await runMeshProxy(env, new Request(`${HOST}/v1/mesh`), "/v1/mesh");
assert.equal(meshOp.status, 200);
assert.equal(meshOp.data.ok, true);
assert.equal(meshOp.data.enabled, false);
assert.equal(meshOp.data.code, "MESH-OK");
assert.deepEqual(meshOp.data.rollup, { live: 0, locked: 0, isolated: 0 });
assert.equal(meshOp.data.qns_cd_spec, "QNS-CD-1.0");
assert.equal(meshOp.data.qns_cd.spec, "QNS-CD-1.0");
assert.equal(meshOp.data.qns_cd.public_proxy, false);

const statusOp = await runMeshProxy(env, new Request(`${HOST}/v1/mesh/status`), "/v1/mesh/status");
assert.equal(statusOp.status, 200);
assert.equal(statusOp.data.ok, true);
assert.equal(statusOp.data.enabled, false);
assert.equal(statusOp.data.code, "MESH-OK");

async function worker(path, method, body) {
  const url = new URL(path, HOST);
  const init = { method, headers: { "User-Agent": "Mozilla/5.0", Accept: "application/json" } };
  if (body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }
  const res = await handleRuntime(new Request(url, init), url, env);
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  return { status: res.status, data };
}

const meshHttp = await worker("/v1/mesh", "GET");
assert.equal(meshHttp.status, 200);
assert.equal(meshHttp.data.ok, true);
assert.equal(meshHttp.data.enabled, false);
assert.equal(meshHttp.data.code, "MESH-OK");

const statusHttp = await worker("/v1/mesh/status", "GET");
assert.equal(statusHttp.status, 200);
assert.equal(statusHttp.data.ok, true);
assert.equal(statusHttp.data.enabled, false);
assert.equal(statusHttp.data.code, "MESH-OK");

const enableEmpty = await worker("/v1/mesh/enable", "POST", {});
assert.equal(enableEmpty.status, 400);
assert.equal(enableEmpty.data.code, "MESH-NEED-BEARER");
assert.notEqual(enableEmpty.data.enabled, true);

const enableOk = await worker("/v1/mesh/enable", "POST", { bearer: "suite-presence" });
assert.equal(enableOk.status, 200);
assert.equal(enableOk.data.enabled, true);

const joinOff = await worker("/v1/mesh/join", "POST", { product: "ark" });
assert.equal(joinOff.status, 409);
assert.equal(joinOff.data.code, "MESH-OFF");

assert.ok(seen.some((s) => s.method === "GET" && s.href === `${SERVICE_BINDING_ORIGIN}/v1/mesh`));
assert.ok(seen.some((s) => s.method === "GET" && s.href === `${SERVICE_BINDING_ORIGIN}/v1/mesh/status`));
assert.ok(seen.some((s) => s.method === "POST" && s.path === "/v1/mesh/enable"));

const unknownMesh = await worker("/v1/mesh/gate", "GET");
assert.equal(unknownMesh.status, 404);
assert.equal(unknownMesh.data.code, "MESH-UNKNOWN");

const mcp = await worker("/mcp", "GET");
assert.equal(mcp.status, 200);
assert.equal(mcp.data.mesh.fraggate_slug, "mesh");
assert.equal(mcp.data.mesh.enabled_default, false);
assert.equal(mcp.data.mesh.qns_cd_spec, "QNS-CD-1.0");
assert.equal(mcp.data.mesh.qns_cd.qnsd, false);

console.log("verify-mesh-proxy: /v1/mesh + /v1/mesh/status MESH-OK enabled:false");
