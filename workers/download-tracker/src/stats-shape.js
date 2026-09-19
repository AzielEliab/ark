/**
 * Fleet-copy additive /stats + /count shape for download-tracker Workers.
 *
 * Keep: project, views, downloads, total.
 * Add:  views_human, views_bot, downloads_human, downloads_bot,
 *       human{}, bot{}, classification{method, bot_score_threshold, note}.
 *
 * Invariant: views === views_human + views_bot (same for downloads).
 *
 * Legacy choice (ARK / Whitestone canary): derive the bot bucket on read.
 * Do not reset existing views/downloads. When human/bot KV keys start at 0,
 * views_bot = views - views_human (same for downloads) so the invariant
 * holds. Pre-split traffic is attributed to the bot bucket on read only.
 * Not a one-time KV rewrite. No classification.legacy field.
 *
 * Copy this file into sibling workers/download-tracker/src/.
 * Author: Aziel Eliab only.
 */

import {
  BOT_SCORE_THRESHOLD,
  METHOD_UA_HEALTHCHECK,
  classificationMethod,
} from "./classify.js";

export { BOT_SCORE_THRESHOLD };

export const LEGACY_SPLIT_STRATEGY = "derive-bot-on-read";

export const LEGACY_SPLIT_NOTE =
  "Legacy views/downloads are not reset. human/bot KV keys start at 0; views_bot = views - views_human and downloads_bot = downloads - downloads_human so views === views_human + views_bot (same for downloads). Pre-split traffic is attributed to the bot bucket on read only. When request.cf.botManagement is missing, method is ua+healthcheck and no score is invented. Author: Aziel Eliab only.";

export function splitKeys(project) {
  const p = String(project || "");
  return {
    views: `${p}|__views__`,
    viewsHuman: `${p}|__views_human__`,
    viewsBot: `${p}|__views_bot__`,
    downloads: `${p}|__total__`,
    downloadsHuman: `${p}|__downloads_human__`,
    downloadsBot: `${p}|__downloads_bot__`,
    github: `${p}|__github__`,
  };
}

export function isStatsMetaKey(name, project) {
  if (!name) return true;
  const keys = splitKeys(project);
  return Object.values(keys).includes(name);
}

export function nonnegInt(value) {
  const n = typeof value === "number" ? value : parseInt(value, 10);
  if (!Number.isFinite(n) || n <= 0) return 0;
  return Math.floor(n);
}

/**
 * Derive the bot bucket so total === human + bot even when split keys are 0.
 * Uses stored bot only when it already completes the invariant.
 */
export function deriveBotBucket(total, human, storedBot) {
  const t = nonnegInt(total);
  let h = nonnegInt(human);
  if (h > t) h = t;
  const stored = nonnegInt(storedBot);
  const bot = h + stored === t ? stored : t - h;
  return { total: t, human: h, bot };
}

export function classificationBlock(request) {
  const method = classificationMethod(request);
  const note = method === METHOD_UA_HEALTHCHECK
    ? LEGACY_SPLIT_NOTE
    : "Legacy views/downloads are not reset. human/bot KV keys start at 0; views_bot = views - views_human and downloads_bot = downloads - downloads_human so views === views_human + views_bot (same for downloads). Pre-split traffic is attributed to the bot bucket on read only. Counted GETs use health-check UA, then cf.botManagement verifiedBot or score<=30, then UA denylist; else human. Author: Aziel Eliab only.";
  return {
    method,
    bot_score_threshold: BOT_SCORE_THRESHOLD,
    note,
  };
}

export function shapeAdditiveFields({
  project,
  views,
  downloads,
  total,
  views_human,
  views_bot,
  downloads_human,
  downloads_bot,
  classification,
}) {
  const v = deriveBotBucket(views, views_human, views_bot);
  const d = deriveBotBucket(downloads, downloads_human, downloads_bot);
  return {
    project,
    views: v.total,
    downloads: d.total,
    total: nonnegInt(total),
    views_human: v.human,
    views_bot: v.bot,
    downloads_human: d.human,
    downloads_bot: d.bot,
    human: { views: v.human, downloads: d.human },
    bot: { views: v.bot, downloads: d.bot },
    classification,
  };
}

/** /count keeps project, views, downloads, total first, then the additive split. */
export function shapeCount(base) {
  const add = shapeAdditiveFields(base);
  return {
    project: add.project,
    views: add.views,
    downloads: add.downloads,
    total: add.total,
    views_human: add.views_human,
    views_bot: add.views_bot,
    downloads_human: add.downloads_human,
    downloads_bot: add.downloads_bot,
    human: add.human,
    bot: add.bot,
    classification: add.classification,
  };
}

/** /stats keeps project, total, views, downloads, then the additive split. */
export function shapeStats(base, extra = {}) {
  const add = shapeAdditiveFields(base);
  return {
    project: add.project,
    total: add.total,
    views: add.views,
    downloads: add.downloads,
    views_human: add.views_human,
    views_bot: add.views_bot,
    downloads_human: add.downloads_human,
    downloads_bot: add.downloads_bot,
    human: add.human,
    bot: add.bot,
    classification: add.classification,
    ...extra,
  };
}

export async function readSplitCounters(env, project) {
  const keys = splitKeys(project);
  const get = async (key) => nonnegInt(await env.DOWNLOADS.get(key));
  return {
    views: await get(keys.views),
    views_human: await get(keys.viewsHuman),
    views_bot: await get(keys.viewsBot),
    downloads_human: await get(keys.downloadsHuman),
    downloads_bot: await get(keys.downloadsBot),
  };
}

export async function incrementSplitKey(env, key) {
  const n = nonnegInt(await env.DOWNLOADS.get(key)) + 1;
  await env.DOWNLOADS.put(key, String(n));
  return n;
}
