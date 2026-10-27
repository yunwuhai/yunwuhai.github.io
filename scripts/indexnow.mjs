#!/usr/bin/env node
/**
 * 把「最近更新过的页面」通过 IndexNow 推送给 Bing / Yandex / Seznam / Naver。
 * （Google 不参与 IndexNow，只认 sitemap + 抓取。）
 *
 * 关于 key 是否会被别人看到：
 *   IndexNow 的 key 不是机密。它只是一个「我拥有这个域名」的标记，
 *   必须能通过 https://<host>/<key>.txt 公开访问，搜索引擎会主动去读这个文件。
 *   别人拿到 key 最多只能替你提交本域名下的 URL，改不了站、也读不到任何数据；
 *   各引擎都有频率限制，恶意刷会被忽略。想换 key：删掉 static/<旧key>.txt，
 *   重新生成一个 <新key>.txt（32 位十六进制）即可，旧 key 立即失效。
 *   文档：https://www.indexnow.org/documentation
 */
import { readdirSync } from "node:fs";
import { basename } from "node:path";

const HOST = "blog.yunwuhai.com";
const SITEMAP = `https://${HOST}/sitemap.xml`;
// 只推最近 N 天内「更新过」的页面，避免每次部署都把全部文章重推一遍
const MAX_AGE_DAYS = Number(process.env.INDEXNOW_MAX_AGE_DAYS || 3);
const MAX_URLS = 10000; // 单次请求上限
const RETRIES = 6;
const RETRY_DELAY_MS = 15000;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function extractFreshUrls(xml, cutoff) {
  const urls = [];
  for (const m of xml.matchAll(/<url>([\s\S]*?)<\/url>/g)) {
    const block = m[1];
    const loc = (block.match(/<loc>([^<]+)<\/loc>/) || [])[1];
    const lastmod = (block.match(/<lastmod>([^<]+)<\/lastmod>/) || [])[1];
    if (!loc) continue;
    const ts = lastmod ? Date.parse(lastmod) : NaN;
    if (Number.isFinite(ts) && ts >= cutoff) urls.push(loc);
  }
  return urls.slice(0, MAX_URLS);
}

async function main() {
  const keyFile = readdirSync("static").find((f) => /^[0-9a-f]{32}\.txt$/.test(f));
  if (!keyFile) {
    console.log("IndexNow: static/ 下找不到 <32位hex>.txt 形式的 key 文件，跳过");
    return;
  }
  const key = basename(keyFile, ".txt");
  const keyLocation = `https://${HOST}/${key}.txt`;
  const cutoff = Date.now() - MAX_AGE_DAYS * 86400_000;

  let urls = [];
  for (let attempt = 1; attempt <= RETRIES; attempt++) {
    try {
      // 加时间戳 + no-cache：Pages 的 CDN 会缓存 sitemap 几分钟
      const res = await fetch(`${SITEMAP}?cb=${Date.now()}`, { headers: { "cache-control": "no-cache" } });
      if (!res.ok) throw new Error(`sitemap HTTP ${res.status}`);
      urls = extractFreshUrls(await res.text(), cutoff);
      if (urls.length > 0) break;
      console.log(`IndexNow: 第 ${attempt}/${RETRIES} 次没读到新页面，${RETRY_DELAY_MS / 1000}s 后重试…`);
    } catch (err) {
      console.log(`IndexNow: 读取 sitemap 失败（${err.message}），${RETRY_DELAY_MS / 1000}s 后重试…`);
    }
    if (attempt < RETRIES) await sleep(RETRY_DELAY_MS);
  }

  if (urls.length === 0) {
    console.log(`IndexNow: 最近 ${MAX_AGE_DAYS} 天没有更新页面，跳过提交`);
    return;
  }

  console.log(`IndexNow: 准备提交 ${urls.length} 个 URL（key ${key}）`);
  for (const u of urls.slice(0, 20)) console.log("  " + u);
  if (urls.length > 20) console.log(`  …（共 ${urls.length} 个）`);

  if (process.env.INDEXNOW_DRY_RUN) {
    console.log("IndexNow: DRY RUN，不发送请求");
    return;
  }

  const res = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({ host: HOST, key, keyLocation, urlList: urls }),
  });
  console.log(`IndexNow: HTTP ${res.status} ${res.statusText}`);
  if (![200, 202].includes(res.status)) {
    process.exitCode = 1;
  }
}

// 不调用 process.exit()：Node 24 在 keep-alive 连接未关闭时强制退出会触发 libuv 断言
main().catch((err) => {
  console.error("IndexNow: 失败 " + (err && err.stack ? err.stack : err));
  process.exitCode = 1;
});
