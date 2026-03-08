const fs = require('fs');

function parseCSVLine(line) {
    const result = [];
    let cur = "";
    let inQuote = false;
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"' && (i === 0 || line[i - 1] !== '\\')) {
            inQuote = !inQuote;
        } else if (char === ',' && !inQuote) {
            result.push(cur.replace(/^"|"$/g, ''));
            cur = "";
        } else {
            cur += char;
        }
    }
    result.push(cur.replace(/^"|"$/g, ''));
    return result;
}

const fileContent = fs.readFileSync('data/brand_posts.csv', 'utf-8');
const lines = fileContent.split(/\r?\n/).filter(line => line.trim() !== "");
console.log("Lines length:", lines.length);

if (lines.length > 1) {
    const row = parseCSVLine(lines[1]);
    console.log("Row length:", row.length);
    console.log("Row contents:", row);
}

