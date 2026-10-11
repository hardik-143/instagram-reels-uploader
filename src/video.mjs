import { closeSync, openSync, readSync, statSync } from 'node:fs';

export function assertMp4(path) {
  const size = statSync(path).size;
  if (size < 12 || size > 300 * 1024 * 1024) throw new Error('Video must be a nonempty MP4 under 300 MiB');
  const header = Buffer.alloc(12);
  const fd = openSync(path, 'r');
  try { readSync(fd, header, 0, header.length, 0); }
  finally { closeSync(fd); }
  if (header.toString('ascii', 4, 8) !== 'ftyp') throw new Error('Video is not an MP4 file. Confirm Git LFS downloaded the actual video.');
}
