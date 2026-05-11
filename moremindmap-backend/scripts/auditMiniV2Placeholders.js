const fs = require('fs');
const path = require('path');

const templateDir = path.join(__dirname, '../templates/mini-v2');
const htmlFiles = fs.readdirSync(templateDir).filter(file => file.endsWith('.html'));

if (htmlFiles.length === 0) {
  console.log("NO MINI V2 TEMPLATES FOUND");
  // Optionally, you could also create an empty GAP_REPORT here if templates are missing
  // fs.writeFileSync(path.join(__dirname, '../MINI_V2_PLACEHOLDER_GAP_REPORT.md'), '# NO MINI V2 TEMPLATES FOUND\n');
  process.exit(1); // Exit with an error code if no templates are found
}

const placeholderContract = {};
const gapReportLines = ['# Mini V2 Placeholder Gap Report\n'];

htmlFiles.forEach(file => {
  const filePath = path.join(templateDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  const placeholders = content.match(/{{(.*?)}}/g);

  if (placeholders) {
    placeholders.forEach(ph => {
      const placeholderName = ph.replace(/[{}]/g, '').trim();
      placeholderContract[placeholderName] = { found: true, file: file };
      gapReportLines.push(`- Placeholder \'${placeholderName}\' found in ${file}`);
    });
  } else {
    gapReportLines.push(`- No placeholders found in ${file}`);
  }
});

// Ensure the scripts directory and its parent exist
// This check is more robust in case the script is run from a different context
const scriptDir = path.join(__dirname);
const backendDir = path.join(scriptDir, '..');
const reportPath = path.join(backendDir, 'MINI_V2_PLACEHOLDER_GAP_REPORT.md');
const contractPath = path.join(backendDir, 'MINI_V2_PLACEHOLDER_CONTRACT.json');

// Write the contract JSON
fs.writeFileSync(contractPath, JSON.stringify(placeholderContract, null, 2));

// Write the gap report
fs.writeFileSync(reportPath, gapReportLines.join('\n'));

console.log('Audit complete. Contract and gap report generated.');

process.exit(0); // Exit successfully
