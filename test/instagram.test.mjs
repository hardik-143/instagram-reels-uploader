import test from 'node:test';
import assert from 'node:assert/strict';
import { createContainer, publishContainer, containerStatus } from '../src/instagram.mjs';

test('creates, checks, and publishes a Reel through Instagram Login endpoints', async () => {
  const originalFetch = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options = {}) => {
    calls.push({ url: String(url), options });
    return { ok: true, json: async () => ({ id: '123', status_code: 'FINISHED' }) };
  };
  try {
    await createContainer('42', 'secret-token', 'https://example.test/video.mp4', 'Hello #reels');
    await containerStatus('123', 'secret-token');
    await publishContainer('42', '123', 'secret-token');
    assert.equal(calls[0].url, 'https://graph.instagram.com/v26.0/42/media');
    assert.equal(calls[0].options.body.get('media_type'), 'REELS');
    assert.equal(calls[0].options.body.get('video_url'), 'https://example.test/video.mp4');
    assert.equal(calls[1].url, 'https://graph.instagram.com/v26.0/123?fields=status_code,status');
    assert.equal(calls[2].url, 'https://graph.instagram.com/v26.0/42/media_publish');
    assert.equal(calls[2].options.body.get('creation_id'), '123');
  } finally {
    globalThis.fetch = originalFetch;
  }
});
