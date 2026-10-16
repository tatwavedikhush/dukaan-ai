import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));
const port = Number(process.env.PORT || 3000);
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8' };

const server = http.createServer(async (request, response) => {
  const requested = request.url === '/' ? '/public/index.html' : `/public${request.url}`;
  const safePath = requested.replace(/\.\.+/g, '');
  try {
    const body = await readFile(join(root, safePath));
    response.writeHead(200, { 'Content-Type': types[extname(safePath)] || 'text/plain; charset=utf-8' });
    response.end(body);
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Not found');
  }
});

server.listen(port, () => console.log(`DukaanAI running at http://localhost:${port}`));
