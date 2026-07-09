# Suyash Mishra — personal site

A personal site + blog + publications list, built with Jekyll and hosted free on
GitHub Pages. GitHub builds and publishes it for you — **you never need to install
anything.** To publish, you commit files. To write, you add a Markdown file.

---

## 1. Put it online (about 5 minutes)

You have two choices for the web address.

### Option A — the clean address `https://YOURNAME.github.io`  (recommended)

1. Create a GitHub account if you don't have one.
2. Create a **new repository** named exactly `YOURNAME.github.io`
   (replace `YOURNAME` with your GitHub username — it must match).
3. Upload every file from this folder into that repo.
   - Easiest in the browser: on the repo page, **Add file → Upload files**,
     drag in everything, then **Commit changes**.
   - Make sure the *contents* go in the repo root — i.e. `_config.yml` should sit
     at the top level of the repo, not inside a subfolder.
4. Open `_config.yml` and set:
   ```yaml
   url: "https://YOURNAME.github.io"
   baseurl: ""
   ```
5. Wait ~1–2 minutes. Your site is live at `https://YOURNAME.github.io`.

### Option B — any repo name, address `https://YOURNAME.github.io/REPO`

1. Create a repo with any name, e.g. `site`.
2. Upload all files (as above).
3. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from a
   branch**, pick branch `main`, folder `/ (root)`, **Save**.
4. Open `_config.yml` and set (the `baseurl` **must** be `/` + the repo name):
   ```yaml
   url: "https://YOURNAME.github.io"
   baseurl: "/site"
   ```
5. Wait ~1–2 minutes. Live at `https://YOURNAME.github.io/site`.

> If the page looks unstyled (no colours/fonts), the `baseurl` is almost always
> the cause — double-check it matches the rule above, commit, and wait a minute.

---

## 2. Make it yours

Open **`_config.yml`** and edit the top block: your name, tagline, and the
social links (email, GitHub, LinkedIn, Scholar, arXiv, ORCID). Leave any link as
`""` to hide it. Commit the change and the site updates automatically.

Rewrite **`about.html`** in your own voice — it's plain Markdown.

---

## 3. Write a blog post

Add a file to the **`_posts`** folder named `YYYY-MM-DD-a-short-title.md`.
Start it with this block (called "front matter") and write below it in Markdown:

```markdown
---
layout: post
title: "Your post title"
subtitle: "One-line description (optional)"
date: 2026-08-01
tags: [research, notes]
reading: "4 min read"   # optional
math: true              # add ONLY if the post uses equations
---

Write your post here in Markdown. Headings with ##, **bold**, lists,
`code`, links — all work.
```

Commit the file → it appears on the site and on the homepage automatically.
Two example posts are in `_posts` already; delete them once you've read them.

- **Code** blocks are highlighted automatically (use triple-backticks + a language).
- **Math**: set `math: true` in the front matter, then use `$x^2$` inline or
  `$$ ... $$` for display equations (MathJax).

---

## 4. Add a paper

Everything on the Papers page comes from one file: **`_data/papers.yml`**.
Copy an existing block, edit the fields, and commit. To also feature a paper on
the homepage, set `featured: true` (keep that to about three).

To host the PDF yourself, drop it in the `papers/` folder and set
`pdf: "/papers/your-file.pdf"`.

---

## 5. (Optional) Preview on your own computer

Not required — GitHub builds the live site. But if you want a local preview:

```bash
gem install bundler
bundle install
bundle exec jekyll serve
# open http://127.0.0.1:4000
```

(Needs Ruby installed. On the live site none of this matters.)

---

## File map

```
_config.yml         ← site settings you edit (name, links, url/baseurl)
index.html          ← homepage
blog.html           ← the writing index
papers.html         ← the publications index (reads _data/papers.yml)
about.html          ← about page (Markdown)
_posts/             ← one Markdown file per blog post
_data/papers.yml    ← your publication list
papers/             ← PDFs you host yourself
_layouts/           ← page templates (rarely touched)
_includes/          ← header, footer, <head> (rarely touched)
assets/             ← CSS, JS, favicon
```
