#!/usr/bin/env bash
# One-time setup. Run by Icarus in his own terminal, from the repo root:
#   bash scripts/setup-github.sh <repo-name> <public|private>
# Needs git and gh (signed in with: gh auth login). Unverified until first run.
set -euo pipefail
NAME="${1:?repo name}"; VIS="${2:?public or private}"

[ -d .git ] || git init -b main
git add AGENTS.md CLAUDE.md CONTRIBUTING.md README.md .gitattributes .gitignore .nojekyll requirements-dev.txt \
  .github/ISSUE_TEMPLATE/goal.md .github/ISSUE_TEMPLATE/bug.md .github/pull_request_template.md .github/workflows/tests.yml \
  .memory/INDEX.md .memory/start.md .memory/directives.md .memory/design.md .memory/his-words.md .memory/decision-map.md \
  .memory/decisions.md .memory/gotchas.md .memory/commands.md .memory/overview.md \
  docs/interface.md mechanism/__init__.py mechanism/constants.py tests/test_smoke.py scripts/setup-github.sh
git commit -m "Set up team system"
gh repo create "$NAME" "--$VIS" --source=. --remote=origin --push

gh label create goal --color 1D76DB --description "One piece of work" --force
gh label create bug --color D73A4A --description "Something works wrong" --force
gh label create "area:mechanism" --color 0E8A16 --description "Python mechanism" --force
gh label create "area:web" --color FBCA04 --description "The page" --force
gh label create "area:content" --color C5DEF5 --description "Words, project page, video" --force
gh label create blocked --color B60205 --description "Cannot continue" --force
gh label create needs-icarus --color 5319E7 --description "Waiting on Icarus" --force

echo "Done. Next: add teammates (gh api -X PUT repos/OWNER/$NAME/collaborators/USERNAME) and create the board."
