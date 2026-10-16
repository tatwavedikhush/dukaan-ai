import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';

const port = 4317;
const server = spawn(process.execPath, ['server.js'], { env: { ...process.env, PORT: String(port) } });
try {
  await new Promise((resolve, reject) => { server.stdout.once('data', resolve); server.once('error', reject); });
  const response = await fetch(`http://127.0.0.1:${port}/`);
  const html = await response.text();
  assert.equal(response.status, 200);
  for (const text of ['DukaanAI', 'Your shop at a glance', 'Add product', 'Products', 'Recent activity']) assert.match(html, new RegExp(text));
  const script = await (await fetch(`http://127.0.0.1:${port}/app.js`)).text();
  assert.match(script, /product-form/);
  console.log('✓ dashboard page and add-product UI are served');
} finally { server.kill(); }
