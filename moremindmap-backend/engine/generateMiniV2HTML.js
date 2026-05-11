import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEMPLATE_DIR = path.resolve(__dirname, '../templates/mini-v2');

const PAGE_FILES = [
 'page01-cover.html',
 'page02-operating-system-map.html',
 'page03-executive-summary.html',
 'page04-operating-pattern.html',
 'page05-decision-architecture.html',
 'page06-communication-style.html',
 'page07-system-under-strain.html',
 'page08-operating-environment-fit.html',
 'page09-facilitator-notes.html',
 'page10-full-profile-unlocks-dna.html'
];

function escapeHtml(value = '') {
 return String(value)
 .replaceAll('&', '&amp;')
 .replaceAll('<', '&lt;')
 .replaceAll('>', '&gt;')
 .replaceAll('"', '&quot;')
 .replaceAll("'", '&#039;');
}

function replacePlaceholders(template, data) {
 return template.replace(/\{\{([^}]+)\}\}/g, (_, rawKey) => {
 const key = rawKey.trim();
 if (Object.prototype.hasOwnProperty.call(data, key)) {
 return escapeHtml(data[key]);
 }
 return `{{${key}}}`;
 });
}

export async function generateMiniV2HTML(data = {}) {
 const pages = [];

 for (const file of PAGE_FILES) {
 const filePath = path.join(TEMPLATE_DIR, file);
 const template = await fs.readFile(filePath, 'utf8');
 pages.push(replacePlaceholders(template, data));
 }

 const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>MORE MindMap Mini Profile V2</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
* {
box-sizing: border-box;
}

body {
margin: 0;
background: #111;
color: #111;
font-family: Inter, Arial, Helvetica, sans-serif;
}

.mmm-page {
width: 8.5in;
min-height: 11in;
margin: 0 auto;
padding: 0.6in;
background: #fff;
page-break-after: always;
break-after: page;
position: relative;
}

.mmm-page h1,
.mmm-page h2,
.mmm-page h3 {
margin-top: 0;
letter-spacing: -0.02em;
}

.mmm-page .eyebrow {
font-size: 11px;
letter-spacing: 0.16em;
text-transform: uppercase;
color: #555;
margin-bottom: 18px;
}

.mmm-grid {
display: grid;
grid-template-columns: 1fr 1fr;
gap: 18px;
}

.mmm-card {
border: 1px solid #ddd;
border-radius: 16px;
padding: 18px;
background: #fafafa;
}

.mmm-footer {
position: absolute;
left: 0.6in;
right: 0.6in;
bottom: 0.35in;
font-size: 10px;
color: #777;
border-top: 1px solid #ddd;
padding-top: 8px;
}

@media print {
body {
background: #fff;
}

.mmm-page {
margin: 0;
width: 8.5in;
min-height: 11in;
}
}
</style>
</head>
<body>
${pages.join('\n\n')}
</body>
</html>`;

 const leftovers = html.match(/\{\{[^}]+\}\}/g) || [];
 if (leftovers.length) {
 throw new Error(`Mini V2 HTML generation failed: ${leftovers.length} placeholders left`);
 }

 const pageCount = (html.match(/class="[^"]*mmm-page[^"]*"/g) || []).length;
 if (pageCount !== 10) {
 throw new Error(`Mini V2 HTML generation failed: expected 10 pages, found ${pageCount}`);
 }

 return html;
}

export default generateMiniV2HTML;

export { generateMiniV2HTML as generateHTML };
