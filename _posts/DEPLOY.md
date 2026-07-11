# Publishing the SHARP blog on GitHub Pages

The blog is a single self-contained file (`docs/index.html`) — all figures are embedded,
and only MathJax (equations) and Mermaid (the flowchart) load from a CDN at view time.
It renders offline except for those two, which need internet in the visitor's browser.

If a GitHub Page shows a blank page, a 404, or your README instead of the blog, it is
almost always one of two things: **Jekyll processing** or **the file being in the wrong place.**
This folder fixes both.

## Fastest path (recommended): serve from `/docs`

1. Put this repository on GitHub (or copy the `docs/` folder into an existing repo).
2. On GitHub: **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Set **Branch** to `main` and the folder to **`/docs`**, then **Save**.
5. Wait ~1 minute. Your blog is live at:
   `https://<your-username>.github.io/<your-repo>/`

That's it. `docs/index.html` is served as the site root, and `docs/.nojekyll`
tells GitHub to skip Jekyll and serve the file exactly as-is.

## Alternative: serve from the repository root

1. Copy `docs/index.html` to the repo root as `index.html`.
2. Make sure the empty `.nojekyll` file is also at the repo root (it is, in this repo).
3. **Settings → Pages → Source → Deploy from a branch → `main` / `/ (root)`**.
4. Live at `https://<your-username>.github.io/<your-repo>/`.

## Alternative: a dedicated `gh-pages` branch

```bash
git checkout --orphan gh-pages
git rm -rf .
cp docs/index.html index.html
touch .nojekyll
git add index.html .nojekyll
git commit -m "Publish SHARP blog"
git push origin gh-pages
```
Then **Settings → Pages → Source → `gh-pages` / `/ (root)`**.

## Common mistakes (why "it won't render")

- **Viewing the blob/raw URL.** `github.com/.../blob/main/docs/index.html` shows the
  *source*, and `raw.githubusercontent.com/...` serves it as plain text. Neither renders.
  Use the **Pages URL** (`https://<user>.github.io/<repo>/`).
- **No `.nojekyll`.** Jekyll can mangle or skip static files; the empty `.nojekyll`
  file disables it. It is included here.
- **Wrong Pages source.** If Pages is set to the repo root but the HTML is in `/docs`
  (or vice versa), you get a 404 or the README. Match the setting to where the file is.
- **Corporate network / ad-blockers** may block `cdn.jsdelivr.net`. If so, equations and
  the flowchart won't render, but the text still will. To make it 100% offline, self-host
  MathJax and Mermaid and update the two `<script>`/`import` URLs in `index.html`.
