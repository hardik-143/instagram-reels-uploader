import { createHash } from 'node:crypto';
import { appendFileSync, copyFileSync, createReadStream, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { loadEnv, required } from './env.mjs';
import { containerStatus, createContainer, publishedMedia, publishContainer } from './instagram.mjs';
import { loadEntry, nextEntry } from './queue.mjs';
import { assertMp4 } from './video.mjs';

loadEnv();
const dryRun = process.argv.includes('--dry-run');
const slug = process.argv.find((arg) => !arg.startsWith('--') && arg !== process.argv[0] && arg !== process.argv[1]);
const entry = slug ? loadEntry(slug) : nextEntry();
if (!entry) {
  console.log('Queue is empty.');
  process.exit(0);
}
if (entry.status?.phase === 'published') throw new Error(`${entry.slug} was already published`);
assertMp4(entry.videoPath);

const hash = createHash('sha256');
for await (const chunk of createReadStream(entry.videoPath)) hash.update(chunk);
const videoHash = hash.digest('hex');
const captionHash = createHash('sha256').update(entry.caption).digest('hex');
if (entry.status && (entry.status.videoHash !== videoHash || entry.status.captionHash !== captionHash)) throw new Error(`${entry.slug}: video or caption changed after publishing began`);
if (dryRun) {
  console.log(JSON.stringify({ slug: entry.slug, queuedAt: entry.metadata.queuedAt, caption: entry.caption, videoHash, phase: entry.status?.phase || 'queued' }, null, 2));
  process.exit(0);
}

const token = required('IG_ACCESS_TOKEN');
const userId = required('IG_USER_ID');
const repository = required('GITHUB_REPOSITORY');
const branch = required('GITHUB_REF_NAME');
if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository)) throw new Error('Invalid GITHUB_REPOSITORY');
const releaseTag = 'instagram-media-host';
const assetName = `${entry.slug}-${videoHash.slice(0, 16)}.mp4`;
const assetUrl = `https://github.com/${repository}/releases/download/${releaseTag}/${assetName}`;

function gh(...args) {
  return execFileSync('gh', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function git(...args) {
  return execFileSync('git', args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function persist(status) {
  writeFileSync(entry.statusPath, `${JSON.stringify(status, null, 2)}\n`);
  git('add', entry.statusPath);
  git('-c', 'user.name=github-actions[bot]', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com', 'commit', '-m', `chore: record Instagram ${status.phase} for ${entry.slug}`);
  git('pull', '--rebase', 'origin', branch);
  git('push', 'origin', `HEAD:${branch}`);
  entry.status = status;
}

function baseStatus() {
  return { videoHash, captionHash, releaseAsset: assetName, containerId: entry.status?.containerId, phase: entry.status?.phase };
}

async function waitUntilReady(containerId) {
  for (let attempt = 0; attempt < 60; attempt++) {
    const result = await containerStatus(containerId, token);
    if (result.status_code === 'FINISHED' || result.status_code === 'PUBLISHED') return result.status_code;
    if (result.status_code === 'ERROR' || result.status_code === 'EXPIRED') throw new Error(`Meta container ${containerId}: ${result.status_code} ${result.status || ''}`);
    await new Promise((resolve) => setTimeout(resolve, 10_000));
  }
  throw new Error('Meta did not finish processing the Reel within 10 minutes');
}

async function finishPublished(mediaId = null) {
  if (!mediaId) throw new Error('Instagram published the Reel, but its media ID is unknown. Find the Reel in Instagram and record its URL manually; do not retry media_publish.');
  let postUrl;
  for (let attempt = 0; attempt < 6; attempt++) {
    try {
      const media = await publishedMedia(mediaId, token);
      if (media.permalink) { postUrl = media.permalink; break; }
    } catch (error) {
      if (attempt === 5) throw error;
    }
    if (attempt < 5) await new Promise((resolve) => setTimeout(resolve, 5_000));
  }
  if (!postUrl) throw new Error(`Instagram did not return a permalink for media ${mediaId}; retry this job to save its link without reposting.`);
  persist({ ...baseStatus(), phase: 'published', done: true, mediaId, postUrl, publishedAt: new Date().toISOString() });
  if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, `### Published Reel\n\n[${entry.slug}](${postUrl}) — ${postUrl}\n`);
  try { gh('release', 'delete-asset', releaseTag, assetName, '--yes', '--repo', repository); }
  catch (error) { console.warn(`Published, but temporary asset cleanup failed: ${error.message}`); }
  console.log(`Published ${entry.slug}: ${postUrl}`);
}

if (!entry.status) {
  try { gh('release', 'view', releaseTag, '--repo', repository); }
  catch { gh('release', 'create', releaseTag, '--repo', repository, '--title', 'Temporary Instagram media', '--notes', 'Assets are removed after Instagram confirms publication.', '--latest=false'); }
  const uploadDir = mkdtempSync(join(tmpdir(), 'instagram-reel-'));
  try {
    const uploadPath = join(uploadDir, assetName);
    copyFileSync(entry.videoPath, uploadPath);
    gh('release', 'upload', releaseTag, uploadPath, '--clobber', '--repo', repository);
  } finally {
    rmSync(uploadDir, { recursive: true, force: true });
  }
  let available = false;
  for (let attempt = 0; attempt < 6; attempt++) {
    const head = await fetch(assetUrl, { method: 'HEAD' });
    if (head.ok) { available = true; break; }
    if (attempt < 5) await new Promise((resolve) => setTimeout(resolve, 5_000));
  }
  if (!available) throw new Error('Public release asset is unavailable to Meta');
  const created = await createContainer(userId, token, assetUrl, entry.caption);
  if (!created.id) throw new Error('Meta did not return a container ID');
  persist({ ...baseStatus(), phase: 'container_created', containerId: created.id });
}

if (entry.status.phase === 'publish_requested') {
  const result = await containerStatus(entry.status.containerId, token);
  if (result.status_code === 'PUBLISHED') await finishPublished(entry.status.mediaId);
  else throw new Error('Publish result is uncertain. Check Instagram manually before retrying; this job will not post a duplicate.');
} else if (entry.status.phase === 'container_created') {
  const current = await waitUntilReady(entry.status.containerId);
  if (current === 'PUBLISHED') await finishPublished(entry.status.mediaId);
  else {
    persist({ ...baseStatus(), phase: 'publish_requested', requestedAt: new Date().toISOString() });
    const published = await publishContainer(userId, entry.status.containerId, token);
    if (!published.id) throw new Error('Meta did not return a published media ID');
    persist({ ...baseStatus(), phase: 'media_published', mediaId: published.id });
    await finishPublished(published.id);
  }
} else if (entry.status.phase === 'media_published') {
  await finishPublished(entry.status.mediaId);
} else {
  throw new Error(`Unknown status phase: ${entry.status.phase}`);
}
