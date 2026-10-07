// 빌드 시 package.json 버전을 sw.js에 반영
const { readFileSync, writeFileSync } = require('fs');
const { join } = require('path');

try {
  // Read package.json
  const packageJson = JSON.parse(readFileSync(join(__dirname, 'package.json'), 'utf8'));
  const version = packageJson.version;

  // Read sw.js
  const swPath = join(__dirname, 'public', 'sw.js');
  let swContent = readFileSync(swPath, 'utf8');

  // Update version in sw.js
  swContent = swContent.replace(
    /\/\/ Version: .*? \(auto-generated from package\.json\)\nconst APP_VERSION = '.*?';/,
    `// Version: ${version} (auto-generated from package.json)\nconst APP_VERSION = '${version}';`
  );

  writeFileSync(swPath, swContent, 'utf8');

  console.log(`✓ Service Worker version updated to ${version}`);
} catch (error) {
  console.error('✗ Failed to update Service Worker version:', error.message);
  process.exit(1);
}
