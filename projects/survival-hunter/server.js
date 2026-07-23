const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8769;
const FILE = path.join(__dirname, 'index.html');

const server = http.createServer((req, res) => {
  const html = fs.readFileSync(FILE, 'utf8');
  // Inject a unique cache-buster comment
  const busted = html.replace('</head>', `<!-- v${Date.now()} --></head>`);
  res.writeHead(200, {
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0',
    'Surrogate-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff'
  });
  res.end(busted);
});

server.listen(PORT, () => console.log(`http://localhost:${PORT}`));
