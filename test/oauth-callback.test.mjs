import test from 'node:test';
import assert from 'node:assert/strict';
import { authorizationCodeFromRedirect } from '../src/oauth-callback.mjs';

const redirect = 'https://hardik-143.github.io/instagram-reels-uploader/callback/';

test('accepts only the expected Instagram callback URL and state', () => {
  assert.equal(authorizationCodeFromRedirect(`${redirect}?code=abc123&state=nonce`, redirect, 'nonce'), 'abc123');
  assert.throws(() => authorizationCodeFromRedirect('https://other.example/callback/?code=abc123&state=nonce', redirect, 'nonce'), /does not match/);
  assert.throws(() => authorizationCodeFromRedirect(`${redirect}?code=abc123&state=other`, redirect, 'nonce'), /state/);
  assert.throws(() => authorizationCodeFromRedirect(`${redirect}?state=nonce`, redirect, 'nonce'), /missing/);
});
