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
/* Shared CSS System for Mini V2 - Polished for Anchor Pages */

/* Typography */
body {
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  margin: 0;
  padding: 0;
  background-color: #f8f8f8; /* Light gray background */
}

h1, h2, h3 {
  margin-top: 0;
  letter-spacing: -0.02em;
  color: #222;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
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
  margin: 20px auto;
  background-color: #fff;
  padding: 0.6in;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
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
  margin-bottom: 30px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.header-left, .header-right {
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

/* Card System Enhancements */
.mmm-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 18px;
  background: #fdfdfd;
  margin-bottom: 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.three-card-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.development-priority-banner {
  background-color: #f0f0f0;
  padding: 15px 20px;
  border-radius: 8px;
  border-left: 4px solid #D4AF37;
  margin-top: 25px;
}

.development-priority-banner .card-heading {
  color: #0b2a4a;
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
  font-size: 48px; /* Large title */
  margin-bottom: 5px;
  color: #0b2a4a; /* Navy */
}

.cover-identity .subtitle {
  font-size: 24px;
  font-weight: 500;
  color: #D4AF37; /* Gold */
  margin-bottom: 10px;
}

.profile-signature-card { /* Dark card for signature */
  background-color: #222;
  color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  margin: 0 auto 30px auto; /* Center and add bottom margin */
  max-width: 600px; /* Limit width for readability */
}

.profile-signature-card .card-heading {
  color: #D4AF37; /* Gold heading */
}
.profile-signature-card .card-body {
  color: #eee; /* Lighter text for dark card */
}

.core-edge-narrative {
  max-width: 700px;
  margin: 0 auto;
  font-size: 15px;
  color: #333;
}

/* Page 2 Map Enhancements */
.page02-operating-system-map-page {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center map elements */
}

.operating-system-map {
  margin-top: 40px;
  position: relative;
  width: 100%;
  max-width: 600px; /* Limit map width */
  text-align: center;
}

.map-node { /* Base style for map nodes */
  position: absolute;
  background-color: #fdfdfd;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px 15px;
  font-size: 12px;
  color: #333;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.map-node.core-engine { top: 20%; left: 50%; transform: translateX(-50%); background-color: #0b2a4a; color: white; padding: 15px 20px; font-weight: bold; }
.map-node.driver { top: 40%; left: 20%; }
.map-node.stabilizer { top: 40%; left: 80%; }
.map-node.opposing { top: 60%; left: 50%; transform: translateX(-50%); }

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
  margin-top: 40px;
  padding: 15px;
  background-color: #fff3e0; /* Light orange background */
  border: 1px solid #ffe0b2;
  border-radius: 8px;
  font-size: 13px;
  color: #bf360c; /* Dark orange text */
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

 if (leftovers.length) {
 throw new Error(`Mini V2 HTML generation failed: ${leftovers.length} placeholders left`);
 }

 console.log("HTML generation completed with explicit pages.length validation.");

 return html;
}

export default generateMiniV2HTML;

export { generateMiniV2HTML as generateHTML };
