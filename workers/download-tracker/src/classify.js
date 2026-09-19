/**
 * Fleet-copy visitor classification for download-tracker Workers.
 *
 * Counted GET order (identical Whitestone / ARK canary):
 *   1. Health-check UAs → bot
 *   2. cf.botManagement verifiedBot or score <= BOT_SCORE_THRESHOLD → bot
 *   3. UA denylist → bot
 *   4. Else human
 *   5. If botManagement is missing: UA + health-check only.
 *      classification.method stays honest. Never invent scores.
 *
 * Copy this file into sibling workers/download-tracker/src/.
 * Author: Aziel Eliab only.
 */

export const BOT_SCORE_THRESHOLD = 30;

export const METHOD_CF_UA = "cf-bot-management+ua";
export const METHOD_UA_HEALTHCHECK = "ua+healthcheck";

/** Step 1 — health-check / probe agents. Checked before botManagement. */
export const HEALTHCHECK_UA_NEEDLES = Object.freeze([
  "cf-healthchecks",
  "cloudflare-healthchecks",
  "googlehc/",
  "kube-probe",
  "amazon-route53-health-check",
  "elb-healthchecker",
]);

/**
 * Step 3 — known crawlers / CLI harvest UAs.
 * Includes the fleet denylist plus a few obvious siblings.
 */
export const BOT_UA_DENYLIST = Object.freeze([
  "googlebot",
  "bingbot",
  "gptbot",
  "claudebot",
  "bytespider",
  "petalbot",
  "yandex",
  "semrush",
  "ahrefs",
  "dotbot",
  "curl/",
  "wget/",
  "python-requests",
  "cf-healthchecks",
  "cloudflare-healthchecks",
  "chatgpt-user",
  "anthropic-ai",
  "perplexitybot",
  "amazonbot",
  "baiduspider",
  "duckduckbot",
  "applebot",
  "facebookexternalhit",
  "meta-externalagent",
  "ccbot",
  "mj12bot",
  "blexbot",
]);

function headerGet(headers, name) {
  if (!headers) return "";
  if (typeof headers.get === "function") {
    return headers.get(name) || headers.get(name.toLowerCase()) || "";
  }
  return headers[name] || headers[name.toLowerCase()] || "";
}

export function userAgentOf(request) {
  return String(headerGet(request && request.headers, "user-agent") || "");
}

export function botManagementOf(request) {
  const cf = request && request.cf;
  const bm = cf && cf.botManagement;
  if (!bm || typeof bm !== "object" || Array.isArray(bm)) return null;
  return bm;
}

export function hasBotManagement(request) {
  return botManagementOf(request) != null;
}

export function classificationMethod(request) {
  return hasBotManagement(request) ? METHOD_CF_UA : METHOD_UA_HEALTHCHECK;
}

function uaLower(request) {
  return userAgentOf(request).toLowerCase();
}

function includesNeedle(hay, needles) {
  for (const needle of needles) {
    if (hay.includes(needle)) return needle;
  }
  return null;
}

export function isHealthcheckUa(requestOrUa) {
  const hay = typeof requestOrUa === "string"
    ? requestOrUa.toLowerCase()
    : uaLower(requestOrUa);
  return includesNeedle(hay, HEALTHCHECK_UA_NEEDLES);
}

export function isDeniedBotUa(requestOrUa) {
  const hay = typeof requestOrUa === "string"
    ? requestOrUa.toLowerCase()
    : uaLower(requestOrUa);
  return includesNeedle(hay, BOT_UA_DENYLIST);
}

function realScore(bm) {
  if (!bm || typeof bm.score !== "number" || !Number.isFinite(bm.score)) return null;
  return bm.score;
}

/**
 * Classify one counted request.
 * `score` is a number only when botManagement actually supplied one.
 */
export function classifyRequest(request) {
  const bm = botManagementOf(request);
  const method = classificationMethod(request);
  const score = realScore(bm);
  const health = isHealthcheckUa(request);
  if (health) {
    return { kind: "bot", method, reason: "healthcheck", matched: health, score };
  }

  if (bm) {
    if (bm.verifiedBot === true) {
      return { kind: "bot", method, reason: "verifiedBot", matched: null, score };
    }
    if (score != null && score <= BOT_SCORE_THRESHOLD) {
      return { kind: "bot", method, reason: "score", matched: null, score };
    }
  }

  const denied = isDeniedBotUa(request);
  if (denied) {
    return { kind: "bot", method, reason: "ua-denylist", matched: denied, score };
  }

  return { kind: "human", method, reason: "default-human", matched: null, score };
}
