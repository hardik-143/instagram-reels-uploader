import { createServer } from 'node:http';
import { randomBytes } from 'node:crypto';
import { spawn } from 'node:child_process';
import { loadEnv, required, updateEnv } from './env.mjs';
import { exchangeCode, exchangeLongLived, profile } from './instagram.mjs';

loadEnv();
const appId = required('INSTAGRAM_APP_ID');
const appSecret = required('INSTAGRAM_APP_SECRET');
const redirectUri = process.env.INSTAGRAM_REDIRECT_URI || 'http://localhost:8787/callback';
const callback = new URL(redirectUri);
if (callback.protocol !== 'http:' || !['localhost', '127.0.0.1'].includes(callback.hostname)) throw new Error('Redirect URI must be a local HTTP callback');

const state = randomBytes(24).toString('hex');
const authUrl = new URL('https://www.instagram.com/oauth/authorize');
authUrl.search = new URLSearchParams({
  enable_fb_login: '0',
  force_authentication: '1',
  client_id: appId,
  redirect_uri: redirectUri,
  response_type: 'code',
  scope: 'instagram_business_basic,instagram_business_content_publish',
  state,
}).toString();

let settle;
const codePromise = new Promise((resolve, reject) => { settle = { resolve, reject }; });
const server = createServer((request, response) => {
  const incoming = new URL(request.url, redirectUri);
  if (incoming.pathname !== callback.pathname) {
    response.writeHead(404).end('Not found');
    return;
  }
  if (incoming.searchParams.get('state') !== state) {
    response.writeHead(400).end('Invalid authorization state');
    return;
  }
  const error = incoming.searchParams.get('error') || incoming.searchParams.get('error_reason');
  const code = incoming.searchParams.get('code');
  if (error || !code) {
    response.writeHead(400).end('Instagram authorization was not completed.');
    settle.reject(new Error(error || 'Authorization code missing'));
    return;
  }
  response.writeHead(200, { 'Content-Type': 'text/plain' }).end('Instagram connected. You can close this tab.');
  settle.resolve(code.replace(/#_$/, ''));
});

await new Promise((resolve, reject) => server.once('error', reject).listen(Number(callback.port || 80), callback.hostname, resolve));
const opener = process.platform === 'darwin' ? ['open', [authUrl.toString()]] : process.platform === 'win32' ? ['cmd', ['/c', 'start', authUrl.toString()]] : ['xdg-open', [authUrl.toString()]];
console.log('Open this URL to sign in to Instagram:');
console.log(authUrl.toString());
spawn(opener[0], opener[1], { stdio: 'ignore', detached: true }).on('error', () => {});
const timeout = setTimeout(() => settle.reject(new Error('Instagram login timed out after 5 minutes')), 5 * 60 * 1000);
try {
  const code = await codePromise;
  const short = await exchangeCode({ code, appId, appSecret, redirectUri });
  const long = await exchangeLongLived(short.access_token, appSecret);
  const account = await profile(long.access_token);
  if (!['BUSINESS', 'MEDIA_CREATOR', 'CREATOR'].includes(account.account_type)) throw new Error('A Business or Creator Instagram account is required');
  updateEnv({ IG_ACCESS_TOKEN: long.access_token, IG_USER_ID: String(account.id) });
  console.log(`Connected @${account.username} (${account.account_type}). Token and account ID saved to .env.`);
} finally {
  clearTimeout(timeout);
  server.close();
}
