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
/* Shared CSS System for Mini V2 */

/* Typography */
body {
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  line-height: 1.6;
  color: #333; /* Dark charcoal */
  margin: 0;
  padding: 0;
  background-color: #f8f8f8; /* Light gray background */
}

h1, h2, h3 {
  margin-top: 0;
  letter-spacing: -0.02em;
  color: #222; /* Darker charcoal for headings */
}

.page-title {
  font-size: 36px;
  font-weight: 700; /* Bold */
  margin-bottom: 8px;
}

.subtitle {
  font-size: 18px;
  font-weight: 400;
  color: #555;
  margin-bottom: 20px;
}

.eyebrow {
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #777;
  margin-bottom: 12px;
}

.card-heading {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #222;
}

.card-body {
  font-size: 14px;
  font-weight: 400;
  color: #444;
}

/* Page Shell */
.mmm-page {
  width: 8.5in;
  min-height: 11in;
  margin: 20px auto; /* Center page with some margin */
  background-color: #fff;
  padding: 0.6in; /* Consistent padding */
  box-shadow: 0 0 10px rgba(0,0,0,0.1); /* Subtle shadow for page */
  position: relative; /* For absolute positioning of footer */
  box-sizing: border-box; /* Include padding in width/height */
  page-break-after: always;
  break-after: page;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee; /* Muted rule line */
}

.header-left {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #444;
}

.header-right {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #444;
}

/* Dividers and Accents */
.gold-accent-bar {
  width: 40px;
  height: 4px;
  background-color: #D4AF37; /* Warm gold accent */
  margin-top: 5px;
  margin-bottom: 15px;
  border-radius: 2px;
}

.navy-divider {
  height: 1px;
  background-color: #0b2a4a; /* Navy color */
  margin: 20px 0;
}

/* Body Narrative */
.body-narrative p {
  margin-bottom: 1.2em;
  font-size: 14px;
  color: #333;
}

/* Card System */
.mmm-card {
  border: 1px solid #ddd; /* Light border */
  border-radius: 8px;
  padding: 18px;
  background: #fdfdfd; /* Slightly off-white for cards */
  margin-bottom: 20px; /* Spacing between cards */
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.card-heading {
  font-size: 16px; /* Adjusted for better hierarchy */
  font-weight: 700;
  margin-bottom: 10px; /* More space below heading */
  color: #222;
}

.card-body {
  font-size: 14px;
  font-weight: 400;
  color: #444;
}

.three-card-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.development-priority-banner {
  background-color: #f0f0f0; /* Light gray banner */
  padding: 15px 20px;
  border-radius: 8px;
  border-left: 4px solid #D4AF37; /* Gold accent on the left */
  margin-top: 25px;
}

.development-priority-banner .card-heading {
  color: #0b2a4a; /* Navy for banner heading */
}

/* Grid System */
.mmm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

/* Footer */
.page-footer {
  position: absolute;
  left: 0.6in;
  right: 0.6in;
  bottom: 0.35in;
  font-size: 10px;
  color: #777;
  border-top: 1px solid #ddd; /* Muted rule line */
  padding-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.m-icon {
  font-weight: bold;
  color: #D4AF37; /* Gold accent */
  margin-right: 5px;
}

.page-number-box {
  background-color: #eee; /* Light gray */
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: #333;
}

/* Print Styles */
@media print {
  body {
    background: #fff;
  }
  .mmm-page {
    margin: 0;
    box-shadow: none;
    border: none;
    padding: 0.6in; /* Ensure padding is maintained for print */
  }
  .page-footer {
    position: relative; /* Adjust footer positioning for print */
    bottom: auto;
    left: auto;
    right: auto;
    margin-top: 20px;
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
