# MOREMindMap Source of Truth

## Canonical Git Root

The Git repository root is:

/Users/rrg/.openclaw/workspace

## Project Folder

The MOREMindMap backend project folder is currently:

moremindmap-backend/

This folder is not a nested Git repository. It does not have its own .git directory.

Therefore all Git-tracked MOREMindMap backend paths must be referenced from the Git root with:

moremindmap-backend/

Example:

moremindmap-backend/README_PROJECT_STATE.md

NOT:

README_PROJECT_STATE.md

## Canonical GitHub Remote

Expected remote:

https://github.com/RRG-systems/moremindmap-backend.git

## Required Startup Check

Before every session, run from the Git root:

pwd
git remote -v
git branch --show-current
git status --short
git log --oneline -5
ls -lh moremindmap-backend/README_PROJECT_STATE.md
