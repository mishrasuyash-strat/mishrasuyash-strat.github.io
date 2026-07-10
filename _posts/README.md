# Quorum post — GitHub Pages (fixed rendering)

This build fixes the two things that break on GitHub Pages:

- **Math wasn't rendering.** GitHub Pages runs Jekyll, whose Markdown engine doesn't load a math renderer and doesn't treat `$…$` as math — so `$\eta_k$` showed up as raw text. Here, math is protected from the Markdown pass and rendered client-side by **MathJax** (loaded from CDN). Underscores/backslashes in LaTeX (`\eta_k`, `\Pi_{T\mathcal{M}}`) are preserved exactly.
- **Images weren't loading.** Relative paths like `images/fig1.png` break once Jekyll rewrites the page URL. Here, all figures are **embedded directly in the HTML as base64**, so there are no image paths to break — the page is fully self-contained.

The page is a single `index.html` with a hard white background, plus a `.nojekyll` file that tells GitHub Pages to serve the file **as-is** (no Jekyll processing).

## Deploy

```bash
# in a fresh repo folder containing index.html and .nojekyll
git init -b main
git add index.html .nojekyll
git commit -m "Quorum: white-background post (self-contained)"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Then: repo → **Settings → Pages → Deploy from a branch → main / (root) → Save**.
Live at `https://YOUR_USERNAME.github.io/YOUR_REPO/` in a minute or two. Math and images will render correctly because nothing depends on Jekyll or on external image files.

> Already have the dark blog at `index.html` in that repo? Put this one at a different path (e.g. `notes/index.html`) or in a separate repo so they don't overwrite each other.

## Two things to know

- **MathJax needs internet** (it loads from `cdn.jsdelivr.net`). That's fine for any public GitHub Pages site; readers' browsers fetch it automatically. If you ever need a fully offline page, say so and I'll inline the KaTeX renderer instead.
- **The page is ~1 MB** because the seven figures are embedded. That's normal for an image-rich single page and loads fine; the upside is it can never show a broken image.

## If you specifically want the Markdown route (Jekyll blog)

Viewing the raw `quorum-post.md` on **github.com** (the repo file view) already renders both `$…$` math and relative images — GitHub's native viewer supports them. The breakage only happens on a **published Jekyll Pages site**. To make the *Markdown* render on a Jekyll site you'd need to:

1. Add MathJax to your layout's `<head>` (e.g. in `_layouts/default.html`):
   ```html
   <script>window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]}};</script>
   <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
   ```
2. Put the figures in `/assets/` and reference them as `/assets/fig1.png` (root-absolute) or `{{ '/assets/fig1.png' | relative_url }}`.
3. In `_config.yml`, keep `markdown: kramdown` and `kramdown: { math_engine: mathjax }`.

That works, but it's several moving parts. The self-contained `index.html` above avoids all of it — which is why it's the recommended fix.
