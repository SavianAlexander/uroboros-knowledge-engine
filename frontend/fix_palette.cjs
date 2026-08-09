const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, 'src/components/CommandPalette.tsx');
let content = fs.readFileSync(file, 'utf8');
content = content.replace(/hover:bg-indigo-500\/20/g, 'hover:bg-indigo-100 dark:hover:bg-indigo-500/20');
fs.writeFileSync(file, content);
