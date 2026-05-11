// moremindmap-backend/engine/generateMiniV2HTML.js
// Recreated May 11, 2026

import fs from 'fs';
import path from 'path';

const templateDir = path.join(__dirname, '../templates/mini-v2');
const outputDir = path.join(__dirname, '../temp/reports'); // Assuming a temp/reports dir

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const getTemplateContent = (templateName) => {
  const templatePath = path.join(templateDir, templateName);
  try {
    return fs.readFileSync(templatePath, 'utf-8');
  } catch (error) {
    console.error(`Error reading template ${templateName}: ${error.message}`);
    return null;
  }
};

const fillTemplate = (templateContent, data) => {
  let filledContent = templateContent;
  let remainingPlaceholders = [];

  // Simple string replacement for {{placeholder}}
  for (const key in data) {
    const regex = new RegExp(`{{${key}}}`, 'g');
    filledContent = filledContent.replace(regex, data[key]);
  }

  // Check for remaining placeholders
  const remaining = filledContent.match(/{{(.*?)}}/g);
  if (remaining) {
    remainingPlaceholders = remaining.map(ph => ph.replace(/[{}]/g, '').trim());
  }

  return { filledContent, remainingPlaceholders };
};

const generateHTML = (profileData) => {
  const pageOrder = [
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

  let fullHTML = '<!DOCTYPE html>\n<html>\n<head>\n<title>Mini V2 Profile</title>\n<style>\n';
  // Basic CSS for print-safe, simple structure
  fullHTML += `
  body { font-family: sans-serif; margin: 0; padding: 0; }
  .mmm-page { margin: 20px auto; padding: 20px; border: 1px solid #eee; max-width: 800px; }
  .page01 { border-top: 5px solid #000; }
  footer { margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }
  h1 { font-size: 1.8em; border-bottom: 1px solid #ddd; padding-bottom: 10px; }
  h2 { font-size: 1.3em; margin-top: 20px; }
  p, div { margin-top: 15px; line-height: 1.6; }
  .diagram, .architecture-diagram { background-color: #f9f9f9; border: 1px dashed #ccc; padding: 15px; text-align: center; margin: 15px 0; }
`;
  fullHTML += '</style>\n</head>\n<body>\n';

  let allRemainingPlaceholders = [];

  for (const page of pageOrder) {
    const templateContent = getTemplateContent(page);
    if (!templateContent) continue;

    // Prepare data for the current page
    // This is a simplified approach; a real system would map profileData to page-specific data
    const pageData = {
      ...profileData.general, // General data applies to all pages
      ...profileData[page.replace('.html', '')] || {}, // Page-specific data
      footer: profileData.general.footer || '© MOREMindMap 2026' // Default footer if not provided
    };

    const { filledContent, remainingPlaceholders } = fillTemplate(templateContent, pageData);

    fullHTML += filledContent + '\n';
    if (remainingPlaceholders.length > 0) {
      allRemainingPlaceholders.push(...remainingPlaceholders.map(ph => `${ph} (in ${page})`));
    }
  }

  fullHTML += '</body>\n</html>';

  if (allRemainingPlaceholders.length > 0) {
    console.error("Error: Remaining placeholders found:", allRemainingPlaceholders.join(', '));
    return null; // Indicate failure
  }

  return fullHTML;
};

export const writeHTMLToFile = (htmlContent, filename = 'mini-v2-rebuilt-test.html') => {
  const outputPath = path.join(outputDir, filename);
  try {
    fs.writeFileSync(outputPath, htmlContent);
    console.log(`HTML report written to: ${outputPath}`);
    return outputPath;
  } catch (error) {
    console.error(`Error writing HTML to file: ${error.message}`);
    return null;
  }
};

export default { generateHTML, writeHTMLToFile };
