# Quorum — Research Notes (GitHub Pages)

A single-post blog engineered for shareability: rich link previews (Open Graph / Twitter cards), JSON-LD, sitemap, and GitHub-backed comments via **Giscus**. Publish it on GitHub Pages in ~10 minutes.

## Files
- `index.html` — the write-up, with SEO/social tags + a comments section
- `og-image.png` — the 1200×630 card that shows when the link is shared
- `favicon.svg`, `robots.txt`, `sitemap.xml`, `.nojekyll`
- `configure.sh` — fills in your URLs/IDs in one shot

---

## Step 1 — create the repo and push

```bash
# put all these files in a folder, then:
cd quorum-notes
git init -b main
git add .
git commit -m "Quorum: first write-up"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/quorum-notes.git
git push -u origin main
```

Make the repo **public** (required for free Pages + for Giscus).

## Step 2 — turn on GitHub Pages

Repo → **Settings → Pages** → *Source*: **Deploy from a branch** → **main** / **/ (root)** → **Save**.
Your site appears at `https://YOUR_GITHUB_USERNAME.github.io/quorum-notes/` within a minute or two.

> Want the shorter URL `https://YOUR_GITHUB_USERNAME.github.io/`? Name the repo `YOUR_GITHUB_USERNAME.github.io` instead and set `REPO` to that in `configure.sh`.

## Step 3 — enable comments (Giscus)

1. Repo → **Settings → General → Features** → tick **Discussions**.
2. Install the app: <https://github.com/apps/giscus> → **Install** → select this repo.
3. Go to <https://giscus.app>. Enter `YOUR_GITHUB_USERNAME/quorum-notes`. It will show your **Repository ID** and, after you pick a Discussion **Category** (e.g. *General* or make an *Announcements* one), a **Category ID**. Copy both.

## Step 4 — fill in your details and re-push

Edit the top of `configure.sh` (username, repo, the two Giscus IDs, category), then:

```bash
bash configure.sh
git commit -am "Configure URLs and Giscus"
git push
```

That replaces every `%%BASE_URL%%`, `%%GH_REPO%%`, and `%%GISCUS_*%%` placeholder. Reload your Pages URL — the social card and the comment box are now live. (You can verify the link preview at <https://www.opengraph.xyz> by pasting your URL.)

---

## Getting traction (the distribution part)

The setup above is necessary but not sufficient — reach comes from where and how you post. A few things that actually move the needle:

- **Lead with the hook, not the brand.** The title "When is a reasoning certificate expensive to fake?" is the share text; keep it. Curiosity + concrete stakes beats jargon.
- **Post where the audience argues about this.** Hacker News (*Show HN* is wrong here; submit as a normal link with the title as-is), r/MachineLearning (flair: Research/Discussion), the LessWrong / Alignment Forum crowd, and X/Bluesky threads tagging the interpretability community. The Giscus comments capture discussion that would otherwise scatter.
- **Give the first comment yourself.** Seed the thread with the single sharpest open question (the O1 computational core) so readers have an obvious thing to react to. Threads with an existing comment get far more replies.
- **Cross-post with a canonical link.** If you also put it on Medium / dev.to / Substack, set the canonical URL to your Pages URL so SEO credit consolidates and you don't split the conversation.
- **One image does the heavy lifting.** The og-image is what people see in the feed; it's designed to read at thumbnail size. If you write a follow-up post, generate a fresh card so each share looks distinct.
- **Invite critique explicitly.** The page already says "proof or refutation welcome." People engage more with an argument that asks to be attacked than one that asks to be admired.

## Adding more posts later

For a second write-up, either replace `index.html` (single evolving post) or move to a folder-per-post layout (`/posts/<slug>/index.html`) with a small home page that lists them — ask and I'll generate the second article + an index in the same style, plus updated sitemap entries.
