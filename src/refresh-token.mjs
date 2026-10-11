import { spawnSync } from 'node:child_process';
import { loadEnv, required, updateEnv } from './env.mjs';
import { refreshToken } from './instagram.mjs';

loadEnv();
const refreshed = await refreshToken(required('IG_ACCESS_TOKEN'));
if (!refreshed.access_token) throw new Error('Meta did not return a refreshed token');

if (process.env.GITHUB_ACTIONS === 'true') {
  required('GH_SECRETS_WRITE_TOKEN');
  const repository = required('GITHUB_REPOSITORY');
  const result = spawnSync('gh', ['secret', 'set', 'IG_ACCESS_TOKEN', '--repo', repository], {
    input: refreshed.access_token,
    encoding: 'utf8',
    env: { ...process.env, GH_TOKEN: process.env.GH_SECRETS_WRITE_TOKEN },
  });
  if (result.status !== 0) throw new Error(`Could not update GitHub secret: ${result.stderr.trim()}`);
  console.log('Instagram token refreshed and GitHub secret updated.');
} else {
  updateEnv({ IG_ACCESS_TOKEN: refreshed.access_token });
  console.log('Instagram token refreshed in .env. Update the GitHub secret as well.');
}
