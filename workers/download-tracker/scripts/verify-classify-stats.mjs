/**
 * Offline additive human/bot /stats + classify check.
 * Author: Aziel Eliab. Apache-2.0.
 */
import assert from "node:assert/strict";
import {
  BOT_SCORE_THRESHOLD,
  METHOD_CF_UA,
  METHOD_UA_HEALTHCHECK,
  classifyRequest,
  classificationMethod,
  hasBotManagement,
} from "../src/classify.js";
import {
  LEGACY_SPLIT_STRATEGY,
  classificationBlock,
  deriveBotBucket,
  isStatsMetaKey,
  shapeCount,
  shapeStats,
  splitKeys,
} from "../src/stats-shape.js";
import worker from "../src/index.js";

assert.equal(BOT_SCORE_THRESHOLD, 30);
assert.equal(LEGACY_SPLIT_STRATEGY, "derive-bot-on-read");
assert.equal(splitKeys("ark").viewsHuman, "ark|__views_human__");
assert.equal(splitKeys("ark").viewsBot, "ark|__views_bot__");
assert.equal(splitKeys("ark").downloadsHuman, "ark|__downloads_human__");
assert.equal(splitKeys("ark").downloadsBot, "ark|__downloads_bot__");
assert.equal(isStatsMetaKey("ark|__views_human__", "ark"), true);
assert.equal(isStatsMetaKey("ark|AzielEliab|ark|main|0", "ark"), false);

function fakeReq(ua, cf) {
  return {
    headers: new Headers(ua ? { "user-agent": ua } : {}),
    cf,
  };
}

// 1. Health-check UA → bot (before botManagement).
const hc = classifyRequest(fakeReq("CF-Healthchecks/1.0", { botManagement: { score: 99, verifiedBot: false } }));
assert.equal(hc.kind, "bot");
assert.equal(hc.reason, "healthcheck");
assert.equal(hc.method, METHOD_CF_UA);
assert.equal(hc.score, 99);

// 2. verifiedBot or score<=30 → bot.
const verified = classifyRequest(fakeReq("Mozilla/5.0", { botManagement: { score: 95, verifiedBot: true } }));
assert.equal(verified.kind, "bot");
assert.equal(verified.reason, "verifiedBot");
const low = classifyRequest(fakeReq("Mozilla/5.0", { botManagement: { score: 30, verifiedBot: false } }));
assert.equal(low.kind, "bot");
assert.equal(low.reason, "score");
assert.equal(low.score, 30);

// 3. UA denylist → bot.
const gpt = classifyRequest(fakeReq("Mozilla/5.0; GPTBot/1.0"));
assert.equal(gpt.kind, "bot");
assert.equal(gpt.reason, "ua-denylist");
assert.equal(gpt.method, METHOD_UA_HEALTHCHECK);
assert.equal(gpt.score, null);
for (const ua of ["Googlebot/2.1", "bingbot", "ClaudeBot", "Bytespider", "PetalBot", "YandexBot", "SemrushBot", "AhrefsBot", "DotBot", "curl/8.0", "Wget/1.21", "python-requests/2.31"]) {
  const got = classifyRequest(fakeReq(ua));
  assert.equal(got.kind, "bot", ua);
  assert.equal(got.reason, "ua-denylist", ua);
}

// 4. Else human.
const human = classifyRequest(fakeReq("Mozilla/5.0"));
assert.equal(human.kind, "human");
assert.equal(human.reason, "default-human");
assert.equal(human.method, METHOD_UA_HEALTHCHECK);
assert.equal(human.score, null);

const humanBm = classifyRequest(fakeReq("Mozilla/5.0", { botManagement: { score: 85, verifiedBot: false } }));
assert.equal(humanBm.kind, "human");
assert.equal(humanBm.score, 85);
assert.equal(humanBm.method, METHOD_CF_UA);

// 5. Missing botManagement: UA+healthcheck only; never invent scores.
assert.equal(hasBotManagement(fakeReq("Mozilla/5.0")), false);
assert.equal(classificationMethod(fakeReq("Mozilla/5.0")), METHOD_UA_HEALTHCHECK);
assert.equal(classifyRequest(fakeReq("Mozilla/5.0")).score, null);
assert.ok(!("score" in classificationBlock(fakeReq("Mozilla/5.0"))));
assert.equal(classificationBlock(fakeReq("Mozilla/5.0")).method, METHOD_UA_HEALTHCHECK);
assert.equal(classificationBlock(fakeReq("Mozilla/5.0")).bot_score_threshold, 30);
assert.equal(
  classificationBlock(fakeReq("Mozilla/5.0", { botManagement: { score: 80, verifiedBot: false } })).method,
  METHOD_CF_UA,
);

// Derive bot bucket so invariant holds when split keys start at 0.
const fresh = deriveBotBucket(166, 0, 0);
assert.deepEqual(fresh, { total: 166, human: 0, bot: 166 });
assert.equal(fresh.total, fresh.human + fresh.bot);

const afterHuman = deriveBotBucket(170, 4, 0);
assert.deepEqual(afterHuman, { total: 170, human: 4, bot: 166 });
assert.equal(afterHuman.total, afterHuman.human + afterHuman.bot);

const afterBoth = deriveBotBucket(172, 4, 2);
assert.deepEqual(afterBoth, { total: 172, human: 4, bot: 168 });
assert.equal(afterBoth.total, afterBoth.human + afterBoth.bot);

const complete = deriveBotBucket(10, 7, 3);
assert.deepEqual(complete, { total: 10, human: 7, bot: 3 });

const count = shapeCount({
  project: "ark",
  views: 166,
  downloads: 64,
  total: 64,
  views_human: 0,
  views_bot: 0,
  downloads_human: 0,
  downloads_bot: 0,
  classification: classificationBlock(fakeReq("Mozilla/5.0")),
});
assert.equal(count.views, 166);
assert.equal(count.views_human, 0);
assert.equal(count.views_bot, 166);
assert.equal(count.downloads, 64);
assert.equal(count.downloads_human, 0);
assert.equal(count.downloads_bot, 64);
assert.equal(count.views, count.views_human + count.views_bot);
assert.equal(count.downloads, count.downloads_human + count.downloads_bot);
assert.deepEqual(count.human, { views: 0, downloads: 0 });
assert.deepEqual(count.bot, { views: 166, downloads: 64 });
assert.equal(count.classification.bot_score_threshold, 30);
assert.match(count.classification.note, /derive|views_bot = views - views_human/i);

const statsShaped = shapeStats({
  project: "ark",
  views: 166,
  downloads: 64,
  total: 64,
  views_human: 0,
  views_bot: 0,
  downloads_human: 0,
  downloads_bot: 0,
  classification: count.classification,
}, { by_repo: { "AzielEliab/ark": 64 } });
assert.equal(statsShaped.project, "ark");
assert.equal(statsShaped.total, 64);
assert.equal(statsShaped.views, statsShaped.views_human + statsShaped.views_bot);
assert.equal(statsShaped.by_repo["AzielEliab/ark"], 64);

function memoryKv(seed = {}) {
  const map = new Map(Object.entries(seed));
  return {
    async get(k) { return map.has(k) ? map.get(k) : null; },
    async put(k, v) { map.set(k, String(v)); },
    async list() {
      return { keys: [...map.keys()].map((name) => ({ name })), list_complete: true };
    },
  };
}

const HOST = "https://ark-download-tracker.vibelock.workers.dev";
const env = {
  DOWNLOADS: memoryKv({
    "ark|__views__": "166",
    "ark|__total__": "64",
    "ark|AzielEliab|ark|main|0": "64",
  }),
  ASSETS: {
    async fetch() {
      return new Response("gzip", { status: 200, headers: { "Content-Length": "4" } });
    },
  },
};

async function hit(path, { method = "GET", ua = "Mozilla/5.0", cf, jsonBody } = {}) {
  const init = { method, headers: { "user-agent": ua, accept: "application/json" } };
  if (jsonBody !== undefined) {
    init.headers["content-type"] = "application/json";
    init.body = JSON.stringify(jsonBody);
  }
  const request = new Request(HOST + path, init);
  if (cf) Object.defineProperty(request, "cf", { value: cf });
  const res = await worker.fetch(request, env);
  const text = await res.text();
  let data = text;
  try { data = text ? JSON.parse(text) : null; } catch { /* keep */ }
  return { status: res.status, data };
}

const before = await hit("/count");
assert.equal(before.status, 200);
assert.equal(before.data.project, "ark");
assert.equal(before.data.views, 166);
assert.equal(before.data.downloads, 64);
assert.equal(before.data.total, 64);
assert.equal(before.data.views_human, 0);
assert.equal(before.data.views_bot, 166);
assert.equal(before.data.downloads_human, 0);
assert.equal(before.data.downloads_bot, 64);
assert.equal(before.data.views, before.data.views_human + before.data.views_bot);
assert.equal(before.data.downloads, before.data.downloads_human + before.data.downloads_bot);
assert.equal(before.data.classification.method, METHOD_UA_HEALTHCHECK);
assert.equal(before.data.classification.bot_score_threshold, 30);

const stats = await hit("/stats");
assert.equal(stats.status, 200);
assert.equal(stats.data.views, 166);
assert.equal(stats.data.views_bot, 166);
assert.equal(stats.data.views, stats.data.views_human + stats.data.views_bot);
assert.equal(stats.data.downloads, stats.data.downloads_human + stats.data.downloads_bot);
assert.deepEqual(stats.data.human, { views: 0, downloads: 0 });
assert.deepEqual(stats.data.bot, { views: 166, downloads: 64 });
assert.equal(stats.data.by_repo["AzielEliab/ark"], 64);

await hit("/", { ua: "Mozilla/5.0" });
const afterHumanView = await hit("/count");
assert.equal(afterHumanView.data.views, 167);
assert.equal(afterHumanView.data.views_human, 1);
assert.equal(afterHumanView.data.views_bot, 166);
assert.equal(afterHumanView.data.views, afterHumanView.data.views_human + afterHumanView.data.views_bot);

await hit("/", { ua: "Googlebot/2.1" });
const afterBotView = await hit("/count");
assert.equal(afterBotView.data.views, 168);
assert.equal(afterBotView.data.views_human, 1);
assert.equal(afterBotView.data.views_bot, 167);
assert.equal(afterBotView.data.views, afterBotView.data.views_human + afterBotView.data.views_bot);

await hit("/download?asset=ark-0.1.0.tar.gz", { ua: "Mozilla/5.0" });
const afterHumanDl = await hit("/count");
assert.equal(afterHumanDl.data.downloads, 65);
assert.equal(afterHumanDl.data.downloads_human, 1);
assert.equal(afterHumanDl.data.downloads_bot, 64);
assert.equal(afterHumanDl.data.downloads, afterHumanDl.data.downloads_human + afterHumanDl.data.downloads_bot);

await hit("/download?asset=ark-0.1.0.tar.gz", { ua: "curl/8.5.0" });
const afterBotDl = await hit("/count");
assert.equal(afterBotDl.data.downloads, 66);
assert.equal(afterBotDl.data.downloads_human, 1);
assert.equal(afterBotDl.data.downloads_bot, 65);
assert.equal(afterBotDl.data.downloads, afterBotDl.data.downloads_human + afterBotDl.data.downloads_bot);

await hit("/download?asset=ark-0.1.0.tar.gz", {
  ua: "Mozilla/5.0",
  cf: { botManagement: { score: 12, verifiedBot: false } },
});
const afterScore = await hit("/count", { cf: { botManagement: { score: 88, verifiedBot: false } } });
assert.equal(afterScore.data.downloads, 67);
assert.equal(afterScore.data.downloads_bot, 66);
assert.equal(afterScore.data.classification.method, METHOD_CF_UA);
assert.equal(afterScore.data.downloads, afterScore.data.downloads_human + afterScore.data.downloads_bot);

const health = await hit("/v1/health");
assert.equal(health.status, 200);
const afterHealth = await hit("/count");
assert.equal(afterHealth.data.views, afterScore.data.views);
assert.equal(afterHealth.data.downloads, afterScore.data.downloads);

console.log("verify-classify-stats: additive human/bot invariant + classify order OK");
