# Instagram Reels uploader

Add one MP4 and one `metadata.json` per folder. GitHub Actions publishes the oldest unposted folder every day at 10:00 AM Asia/Kolkata. The account must be an Instagram Business or Creator account. This uses Meta's official **Instagram API with Instagram Login**, not an Instagram password or browser automation.

## One-time setup

1. Create a **public** GitHub repository named `instagram-reels-uploader` and push this project to its default `main` branch. Public access is required because Meta fetches each video from a temporary GitHub Release asset. Anyone can also see videos committed to this repository.
2. In [Meta for Developers](https://developers.facebook.com/apps/), create an app with **Instagram API with Instagram Login** and configure Business Login for Instagram. Under **Set up Instagram business login → Business login settings**, add `https://hardik-143.github.io/instagram-reels-uploader/callback/` as an exact valid OAuth redirect URI. Request `instagram_business_basic` and `instagram_business_content_publish`. For an app in development mode, add the account as an app tester or role holder and accept the invitation; wider use may require Meta review.
3. Copy `.env.example` to `.env`. Set the **Instagram App ID** and **Instagram App Secret** from the Instagram API setup page, and keep the matching `INSTAGRAM_REDIRECT_URI`. Run `npm run login` on your computer and approve the Instagram prompt. On the callback page, click **Copy callback URL** and paste the URL into the terminal. The helper writes `IG_ACCESS_TOKEN` and `IG_USER_ID` to `.env`. **Never commit `.env`.**
4. In GitHub → repository **Settings → Secrets and variables → Actions**, add `IG_ACCESS_TOKEN` and `IG_USER_ID` from `.env` as repository secrets. Create a fine-grained GitHub personal access token limited to this one repository, with **Secrets: read and write** permission, and store it as `GH_SECRETS_WRITE_TOKEN`. The weekly workflow uses it only to replace `IG_ACCESS_TOKEN` with a refreshed value. Set an expiration and renew this GitHub token before it expires. The built-in `GITHUB_TOKEN` handles release assets and status commits; it cannot update repository secrets.
5. Check the `Publish next Instagram Reel` and `Refresh Instagram token` workflows in the Actions tab. The publish workflow requests `contents: write` for its own job while the repository default can remain read only. If the default branch has protection rules, permit the Actions bot to push `status.json` commits. Run the refresh workflow manually only if your Instagram token is at least 24 hours old.

The Meta app secret stays on your computer; the scheduled jobs do not need it. When the Instagram token is revoked or expires, rerun `npm run login` and replace the two Instagram secrets in GitHub. If the refresh workflow fails, fix it before the token expires.

## Add videos

Claude can create a folder such as:

```text
videos/my-first-reel/
  video.mp4
  metadata.json
```

Example metadata:

```json
{
  "queuedAt": "2026-10-11T04:30:00Z",
  "caption": "A short description of the video.",
  "hashtags": ["#reels", "#example"]
}
```

`queuedAt` is a UTC timestamp used for ordering, not an earliest publish date. The uploader takes one unposted folder per day, sorted by `queuedAt` and then folder name. `caption` is required; `hashtags` is optional and appended to the caption. Keep the combined caption at or under 2,200 characters. Videos must be nonempty MP4 files under 300 MiB and compatible with Meta's Reel video requirements. The repo tracks `videos/*/video.mp4` with Git LFS; install Git LFS before adding files:

```bash
git lfs install
git add videos/my-first-reel
git commit -m "Add first Reel"
git push
```

Check the queue with `npm run queue`; completed entries show `done` and their Instagram link. Use `node src/publish.mjs my-first-reel --dry-run` to see the selected caption and file fingerprint without posting. You can run the publish workflow manually with an optional folder name. A normal run takes the oldest unposted folder.

## Publishing and retries

The workflow fetches only the chosen LFS object, places it on a public GitHub Release, and submits its URL to Meta. It waits for video processing before asking Meta to publish. A `status.json` file beside the video is committed to the default branch. Once posted, it has `phase: "published"`, `done: true`, and `postUrl` with the Instagram Reel link. The Actions run summary also shows the link. The temporary release asset is deleted after confirmed publication; the original video remains in the repository.

If an upload or processing step fails before `media_publish`, the next run resumes the stored container where possible. If a request to `media_publish` has an uncertain result, the job **stops** and asks for manual review rather than risking a duplicate. Confirm the Reel in Instagram and inspect `status.json` and the Meta container before changing its phase. Never delete `status.json` merely to force a retry.

Scheduled workflows run on the default branch and may start later than the exact cron time. A public repository's schedule can be disabled after long inactivity. Monitor the Actions tab and keep GitHub LFS storage and bandwidth available.

## Local checks

```bash
npm test
npm run queue
```

API references: [Meta Instagram API](https://www.postman.com/meta/instagram/folder/6raa77c/instagram-api-with-instagram-login), [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), [GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
