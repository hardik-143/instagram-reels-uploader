import { loadEntry, nextEntry } from './queue.mjs';

const requested = process.argv[2];
const entry = requested ? loadEntry(requested) : nextEntry();
if (entry?.status?.phase === 'published') throw new Error(`${entry.slug} was already published`);
if (entry) process.stdout.write(`${entry.slug}\n`);
