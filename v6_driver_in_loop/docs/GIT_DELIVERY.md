# Safe Git delivery

The original workspace was on `feat/v5-lap-time-simulation` with concurrent,
uncommitted V5 changes. V6 was backed up before editing; the full original source
is retained as `archive/pre_audit_v6.tar.gz`. No stash, reset, clean, V5 staging,
force-push or feature-branch merge is part of this follow-up.

A dedicated `/private/tmp/indy500-v6-engineering` worktree was created on
`feat/v6-driver-in-loop`. After fetching, it was fast-forwarded to stable main
`fe65ddf` before implementation. This is a main-only baseline update; V5 commit
`18b8623` is not an ancestor added to the V6 change. Git writes succeeded through
the execution tool's reviewed permission escalation, resolving the previous
sandbox `.git/index.lock` / branch-lock restriction. The configured remote's
older URL redirects to the verified repository
`fengzhe-li/indy500-racing-point-in-time-decision-support`.

Only `v6_driver_in_loop/` and `.github/workflows/v6.yml` belong in the commit.
The final chat delivery records the resulting commit/PR rather than inventing a
URL in advance. Main is not merged or force-pushed. The active original V5 working
tree remains available for its independent work; final V6 files are copied back
only into its existing V6 directory for local access.

## Reproducible fallback on another Git-enabled machine

If permission/network issues prevent publishing, preserve the V6 source/archive
and the V6 CI file, then use an independent worktree from fetched stable main.
Replace the two source placeholders with the preserved file paths. If the V6
branch already exists, use its existing worktree instead of recreating it.

```bash
git fetch origin main
git worktree add -b feat/v6-driver-in-loop ../indy500-v6-delivery origin/main
cp -R /absolute/path/to/preserved/v6_driver_in_loop ../indy500-v6-delivery/
cp /absolute/path/to/preserved/v6.yml ../indy500-v6-delivery/.github/workflows/v6.yml
cd ../indy500-v6-delivery
python3 -m unittest discover -s v6_driver_in_loop/tests -v
node --test v6_driver_in_loop/viewer/replay.test.mjs
git add -- v6_driver_in_loop .github/workflows/v6.yml
git diff --cached --stat
git diff --cached --name-only
git commit -m "Add audited V6 vehicle simulation and engineering replay"
git push -u origin feat/v6-driver-in-loop
gh pr create --base main --head feat/v6-driver-in-loop --title "V6: audited vehicle dynamics and engineering replay" --body-file /path/to/reviewed-pr-body.md
```

Check the staged names before committing. Do not stage README changes or V5 files
from the concurrent original worktree. A temporary worktree can be deleted by the
operating system; the preserved original workspace and pushed branch are the
durable handoff locations.
