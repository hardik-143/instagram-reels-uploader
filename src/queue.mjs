import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, resolve } from 'node:path';

export const root = resolve('videos');

export function loadEntry(slug) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(slug)) throw new Error(`Invalid slug: ${slug}`);
  const dir = join(root, slug);
  const metadataPath = join(dir, 'metadata.json');
  const videoPath = join(dir, 'video.mp4');
  if (!existsSync(metadataPath) || !existsSync(videoPath)) throw new Error(`${slug}: video.mp4 and metadata.json are both required`);
  const metadata = JSON.parse(readFileSync(metadataPath, 'utf8'));
  if (typeof metadata.caption !== 'string' || !metadata.caption.trim()) throw new Error(`${slug}: caption is required`);
  if (typeof metadata.queuedAt !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(metadata.queuedAt) || Number.isNaN(Date.parse(metadata.queuedAt))) throw new Error(`${slug}: queuedAt must be an ISO UTC timestamp`);
  if (metadata.hashtags !== undefined && (!Array.isArray(metadata.hashtags) || metadata.hashtags.some((tag) => typeof tag !== 'string' || !/^#[\p{L}\p{N}_]+$/u.test(tag)))) throw new Error(`${slug}: hashtags must be an array of #tags`);
  const caption = `${metadata.caption.trim()}${metadata.hashtags?.length ? `\n\n${metadata.hashtags.join(' ')}` : ''}`;
  if (caption.length > 2200) throw new Error(`${slug}: Instagram caption exceeds 2200 characters`);
  const stat = statSync(videoPath);
  if (!stat.isFile() || stat.size === 0 || stat.size > 300 * 1024 * 1024) throw new Error(`${slug}: video must be a nonempty MP4 under 300 MiB`);
  const statusPath = join(dir, 'status.json');
  const status = existsSync(statusPath) ? JSON.parse(readFileSync(statusPath, 'utf8')) : null;
  return { slug, dir, metadata, caption, videoPath, statusPath, status };
}

export function entries() {
  if (!existsSync(root)) return [];
  return readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => loadEntry(entry.name))
    .sort((a, b) => a.metadata.queuedAt.localeCompare(b.metadata.queuedAt) || a.slug.localeCompare(b.slug));
}

export function nextEntry() {
  return entries().find((entry) => entry.status?.phase !== 'published') || null;
}
