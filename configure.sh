#!/usr/bin/env bash
# Fill in your details, then run:  bash configure.sh
set -e
USER="YOUR_GITHUB_USERNAME"      # e.g. suyashmishra
REPO="quorum-notes"              # repo name (or USER.github.io for a user site)
GISCUS_REPO_ID="PASTE_FROM_GISCUS"       # from https://giscus.app after enabling Discussions
GISCUS_CATEGORY="General"                 # a Discussions category (e.g. General or Announcements)
GISCUS_CATEGORY_ID="PASTE_FROM_GISCUS"   # from https://giscus.app

# For a project site the URL is https://USER.github.io/REPO ; for a user site it's https://USER.github.io
if [ "$REPO" = "$USER.github.io" ]; then BASE="https://$USER.github.io"; else BASE="https://$USER.github.io/$REPO"; fi

for f in index.html robots.txt sitemap.xml; do
  sed -i.bak \
    -e "s#%%BASE_URL%%#$BASE#g" \
    -e "s#%%GH_REPO%%#$USER/$REPO#g" \
    -e "s#%%GISCUS_REPO_ID%%#$GISCUS_REPO_ID#g" \
    -e "s#%%GISCUS_CATEGORY%%#$GISCUS_CATEGORY#g" \
    -e "s#%%GISCUS_CATEGORY_ID%%#$GISCUS_CATEGORY_ID#g" \
    "$f" && rm -f "$f.bak"
done
echo "Configured for $BASE"
