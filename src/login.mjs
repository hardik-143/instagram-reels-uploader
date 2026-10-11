import { randomBytes } from 'node:crypto';
import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline/promises';
import { loadEnv, required, updateEnv } from './env.mjs';
import { exchangeCode, exchangeLongLived, profile } from './instagram.mjs';
import { authorizationCodeFromRedirect } from './oauth-callback.mjs';

loadEnv();
const appId = required('INSTAGRAM_APP_ID');
const appSecret = required('INSTAGRAM_APP_SECRET');
const redirectUri = required('INSTAGRAM_REDIRECT_URI');
if (new URL(redirectUri).protocol !== 'https:') throw new Error('INSTAGRAM_REDIRECT_URI must use HTTPS');

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

const opener = process.platform === 'darwin' ? ['open', [authUrl.toString()]] : process.platform === 'win32' ? ['cmd', ['/c', 'start', authUrl.toString()]] : ['xdg-open', [authUrl.toString()]];
console.log('Open this URL to sign in to Instagram:');
console.log(authUrl.toString());
spawn(opener[0], opener[1], { stdio: 'ignore', detached: true }).on('error', () => {});

const prompt = createInterface({ input: process.stdin, output: process.stdout });
let code;
try {
  const returnedUrl = await prompt.question('After approval, copy the full callback URL from the page and paste it here: ');
  code = authorizationCodeFromRedirect(returnedUrl, redirectUri, state);
} finally {
  prompt.close();
}

const short = await exchangeCode({ code, appId, appSecret, redirectUri });
const long = await exchangeLongLived(short.access_token, appSecret);
const account = await profile(long.access_token);
if (!['BUSINESS', 'MEDIA_CREATOR', 'CREATOR'].includes(account.account_type)) throw new Error('A Business or Creator Instagram account is required');
updateEnv({ IG_ACCESS_TOKEN: long.access_token, IG_USER_ID: String(account.id) });
console.log(`Connected @${account.username} (${account.account_type}). Token and account ID saved to .env.`);
