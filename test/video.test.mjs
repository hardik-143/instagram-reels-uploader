import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { assertMp4 } from '../src/video.mjs';

test('rejects a Git LFS pointer in place of an MP4', () => {
  const dir = mkdtempSync(join(tmpdir(), 'reel-video-test-'));
  try {
    const path = join(dir, 'video.mp4');
    writeFileSync(path, 'version https://git-lfs.github.com/spec/v1\n');
    assert.throws(() => assertMp4(path), /not an MP4/);
    writeFileSync(path, Buffer.concat([Buffer.from('0000ftyp0000'), Buffer.alloc(100)]));
    assert.doesNotThrow(() => assertMp4(path));
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
