import { entries } from './queue.mjs';

const all = entries();
for (const entry of all) console.log(`${entry.status?.done ? 'done' : entry.status?.phase || 'queued'}\t${entry.metadata.queuedAt}\t${entry.slug}${entry.status?.postUrl ? `\t${entry.status.postUrl}` : ''}`);
if (!all.length) console.log('Queue is empty.');
