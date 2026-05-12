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

function stripTemplateComments(html) {
 return html.replace(/\{#[\s\S]*?#\}/g, '');
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
 pages.push(stripTemplateComments(replacePlaceholders(template, data)));
 }

 const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>MORE MindMap Mini Profile V2</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
/* Shared CSS System for Mini V2 - Polished for Anchor Pages */

/* Typography */
body {
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  line-height: 1.7;
  color: #2c2c2c;
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
}

h1, h2, h3 {
  margin-top: 0;
  letter-spacing: -0.03em;
  color: #0b2a4a;
  font-weight: 700;
}

.page-title {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 16px;
  color: #0b2a4a;
}

.subtitle {
  font-size: 20px;
  font-weight: 400;
  color: #666;
  margin-bottom: 32px;
  line-height: 1.5;
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
  margin-bottom: 10px;
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
  margin: 30px auto;
  background-color: #fff;
  padding: 0.85in 0.75in;
  box-shadow: 0 2px 20px rgba(0,0,0,0.12);
  position: relative;
  box-sizing: border-box;
  page-break-after: always;
  break-after: page;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48px;
  padding-bottom: 14px;
  border-bottom: 2px solid #e0e0e0;
}

.header-left, .header-right {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #555;
}

/* Dividers and Accents */
.gold-accent-bar {
  width: 60px;
  height: 5px;
  background-color: #D4AF37;
  margin-top: 8px;
  margin-bottom: 24px;
  border-radius: 2px;
}

.navy-divider {
  height: 2px;
  background-color: #0b2a4a;
  margin: 32px 0;
}

/* Card System Enhancements */
.mmm-card {
  border: 1.5px solid #d0d0d0;
  border-radius: 10px;
  padding: 26px;
  background: #fafafa;
  margin-bottom: 24px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}

.three-card-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.development-priority-banner {
  background-color: #f7f7f7;
  padding: 24px 28px;
  border-radius: 10px;
  border-left: 6px solid #D4AF37;
  margin-top: 40px;
}

.development-priority-banner .card-heading {
  color: #0b2a4a;
  font-size: 18px;
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
  border-top: 1px solid #ddd;
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
  background-color: #eee;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: #333;
}

/* Specific Page Enhancements */

/* Page 1 Cover Enhancements */
.page01-cover-page { /* Specific class for cover page main content */
  display: flex;
  flex-direction: column;
  justify-content: center; /* Center content vertically */
  text-align: center;
  padding: 0; /* Reset padding if needed for full bleed cover */
}

.cover-identity {
  margin-bottom: 40px;
}

.cover-identity h1 {
  font-size: 64px;
  margin-bottom: 12px;
  color: #0b2a4a;
  font-weight: 800;
  letter-spacing: -0.04em;
}

.cover-identity .subtitle {
  font-size: 28px;
  font-weight: 500;
  color: #D4AF37;
  margin-bottom: 20px;
}

.profile-signature-card {
  background-color: #1a1a1a;
  color: #fff;
  padding: 42px 48px;
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  margin: 60px auto 50px auto;
  max-width: 680px;
}

.profile-signature-card .card-heading {
  color: #D4AF37; /* Gold heading */
}
.profile-signature-card .card-body {
  color: #eee; /* Lighter text for dark card */
}

.core-edge-narrative {
  max-width: 720px;
  margin: 0 auto;
  padding: 32px;
  font-size: 16px;
  color: #333;
  background: #f9f9f9;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
}

.core-edge-narrative h3 {
  font-size: 22px;
  margin-bottom: 16px;
  color: #0b2a4a;
}

/* Page 2 Map Enhancements */
.page02-operating-system-map-page {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center map elements */
}

.operating-system-map {
  margin-top: 56px;
  position: relative;
  width: 100%;
  min-height: 480px;
  text-align: center;
}

.map-container {
  position: relative;
  width: 100%;
  height: 480px;
}

.map-node {
  position: absolute;
  background-color: #fafafa;
  border: 2px solid #c0c0c0;
  border-radius: 12px;
  padding: 18px 24px;
  font-size: 13px;
  color: #333;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  font-weight: 600;
}

.map-node.core-engine { top: 18%; left: 50%; transform: translateX(-50%); background-color: #0b2a4a; color: white; padding: 24px 32px; font-weight: 700; font-size: 15px; }
.map-node.driver { top: 42%; left: 15%; }
.map-node.stabilizer { top: 42%; left: 85%; transform: translateX(-100%); }
.map-node.opposing { top: 68%; left: 50%; transform: translateX(-50%); }

.map-tension-line {
  position: absolute;
  background-color: #D4AF37; /* Gold accent */
  height: 2px;
  transform-origin: 0 0;
}
.map-tension-line.driver-to-core { top: 35%; left: 35%; width: 30%; height: 2px; transform: rotate(-30deg); }
.map-tension-line.stabilizer-to-core { top: 35%; left: 65%; width: 30%; height: 2px; transform: rotate(30deg); }
.map-tension-line.opposing-to-core { top: 60%; left: 50%; width: 0; height: 170px; /* Vertical line, adjust height */ }

.map-tension-label {
  position: absolute;
  font-size: 10px;
  color: #777;
  background: rgba(255,255,255,0.0); /* Transparent background */
  padding: 2px 5px;
  border-radius: 4px;
}
.map-tension-label.driver { top: 35%; left: 10%; }
.map-tension-label.stabilizer { top: 35%; left: 90%; transform: translateX(-100%); }
.map-tension-label.opposing { top: 75%; left: 50%; transform: translateX(-50%); }

.system-tension-warning {
  margin-top: 56px;
  padding: 24px 28px;
  background-color: #fff8f0;
  border: 2px solid #ffe0b2;
  border-radius: 10px;
  font-size: 14px;
  color: #c63f17;
  line-height: 1.6;
}

.system-tension-warning h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: #bf360c;
}

/* Page 4 Operating Pattern Refinements */
.operating-pattern-page .three-card-row {
  grid-template-columns: repeat(3, 1fr); /* Ensure 3 columns */
  gap: 20px;
}

/* Print Styles - Ensure consistency */
@media print {
  body {
    background: #fff;
  }
  .mmm-page {
    margin: 0;
    box-shadow: none;
    border: none;
    padding: 0.6in;
  }
  .page-footer {
    position: relative;
    bottom: auto;
    left: auto;
    right: auto;
    margin-top: 20px;
  }
  /* Ensure header/footer don't break page flow unexpectedly */
  header, footer {
    position: relative;
  }
}
</style>
</head>
<body>
${pages.join('\n\n')}
</body>
</html>`;

 if (pages.length !== 10) {
 throw new Error(`Mini V2 HTML generation failed: expected 10 page templates, found ${pages.length}`);
 }

 const leftovers = html.match(/\{\{[^}]+\}\}/g) || [];
 if (leftovers.length) {
 throw new Error(`Mini V2 HTML generation failed: ${leftovers.length} placeholders left`);
 }

 console.log("HTML generation completed with explicit pages.length validation.");

 return html;
}

export default generateMiniV2HTML;

export { generateMiniV2HTML as generateHTML };
