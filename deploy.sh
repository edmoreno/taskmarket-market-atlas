#!/bin/sh
set -eu
# Run from this checkout. Uses existing gh authentication; never accepts a token.
repo=${1:?Usage: bash deploy.sh OWNER/NEW-PUBLIC-REPO}
test -d .git || git init -b main
git add .
git diff --cached --quiet || git commit -m 'Publish reproducible Taskmarket Market Atlas'
gh repo create "$repo" --public --source=. --remote=origin
gh api -X POST "repos/$repo/pages" -f build_type=workflow
git push -u origin main
printf 'Deployment started. Inspect with: gh run list --repo %s\n' "$repo"
