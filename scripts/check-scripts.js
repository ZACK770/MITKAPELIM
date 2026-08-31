const fs = require('fs');
const vm = require('vm');

const files = ['index.html', 'admin.html', 'products/spekal.html', 'products/table.html', 'products/beds.html'];

for (const file of files) {
  if (!fs.existsSync(file)) continue;
  const html = fs.readFileSync(file, 'utf8');
  for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (/type=["'](module|application\/ld\+json)/i.test(match[1])) continue;
    if (!match[2].trim()) continue;
    new vm.Script(match[2], { filename: file });
  }
  console.log(file + ' OK');
}

new vm.Script(fs.readFileSync('assets/app-api.js', 'utf8'), { filename: 'assets/app-api.js' });
console.log('assets/app-api.js OK');
