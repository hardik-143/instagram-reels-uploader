import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const original = process.cwd();
const fixture = mkdtempSync(join(tmpdir(), 'reel-queue-test-'));
process.chdir(fixture);
const { entries, nextEntry } = await import('../src/queue.mjs');

function add(slug, queuedAt, status) {
  const dir = join('videos', slug);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'video.mp4'), 'mock video');
  writeFileSync(join(dir, 'metadata.json'), JSON.stringify({ queuedAt, caption: `Caption ${slug}`, hashtags: ['#reels'] }));
  if (status) writeFileSync(join(dir, 'status.json'), JSON.stringify({ phase: status }));
}

test('oldest unposted video is selected and published videos are skipped', () => {
  add('later', '2026-10-12T10:00:00Z');
  add('first', '2026-10-11T10:00:00Z', 'published');
  add('second', '2026-10-11T10:00:00Z');
  assert.deepEqual(entries().map((item) => item.slug), ['first', 'second', 'later']);
  assert.equal(nextEntry().slug, 'second');
});

test('invalid metadata stops the queue', () => {
  add('invalid', 'bad date');
  assert.throws(() => entries(), /queuedAt/);
});

test.after(() => {
  process.chdir(original);
  rmSync(fixture, { recursive: true, force: true });
});
