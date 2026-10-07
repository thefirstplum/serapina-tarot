const fs = require('fs');
const path = require('path');

// Generate build timestamp
const buildTimestamp = Date.now();

// Read and update sw.js
const swPath = path.join(__dirname, 'public', 'sw.js');
let swContent = fs.readFileSync(swPath, 'utf8');

// Replace BUILD_TIMESTAMP value (regex matches any existing value)
swContent = swContent.replace(
  /const BUILD_TIMESTAMP = '.*?';/,
  `const BUILD_TIMESTAMP = '${buildTimestamp}';`
);

fs.writeFileSync(swPath, swContent, 'utf8');

console.log(`✓ Service Worker timestamp updated to ${buildTimestamp}`);

// Also update dist version if it exists
const distSwPath = path.join(__dirname, 'dist', 'sw.js');
if (fs.existsSync(distSwPath)) {
  fs.writeFileSync(distSwPath, swContent, 'utf8');
  console.log(`✓ Dist Service Worker timestamp updated`);
}
