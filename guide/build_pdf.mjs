// 把 guide.html 渲染成 PDF：node guide/build_pdf.mjs
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

// playwright 可能是全局安装的，ESM 不读 NODE_PATH，所以用 require 解析
const { chromium } = createRequire(import.meta.url)('playwright');

const here = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(here, 'guide.html');
const out = path.join(here, '..', '验证码同步设置指南.pdf');

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(pathToFileURL(src).href, { waitUntil: 'networkidle' });
await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
await browser.close();
console.log(`已生成 ${out}`);
