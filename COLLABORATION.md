# Working on this together

Two people, one day. The goal is to never block each other, not to run a software team.

---

## The one real hazard: this folder is inside OneDrive

`Documents/Hackathon` is OneDrive-synced. That is fine for one person as a backup. It is
**actively dangerous for two**, because OneDrive resolves simultaneous edits by creating a
second file with a mangled name — `HANDOVER-DESKTOP-4KJ2X.md` — rather than merging. Two Claude
Code sessions writing to the same synced folder will silently fork your work, and you will not
notice until something you wrote has vanished.

**So: do not both work in a shared OneDrive folder. Use git.** Git merges properly and tells you
when it cannot.

If you see a file with `-DESKTOP-` or `Conflict` in its name, that is OneDrive having forked
something. `.gitignore` excludes those so they never get committed, but you still need to
reconcile them by hand.

---

## Setup (Paul, once)

The repo is already initialised and committed locally on branch `main`. To put it on GitHub:

```bash
cd "C:/Users/green/OneDrive/Documents/Hackathon"
gh repo create hackathon-2026 --private --source=. --remote=origin --push
gh repo invite <julie-github-username> --repo <you>/hackathon-2026
```

**Keep it private.** The ADRI data is CC BY-NC — non-commercial only, attribution required. A
private repo avoids any question about redistribution over the weekend.

## Setup (Julie, once)

```bash
git clone https://github.com/<paul>/hackathon-2026.git
cd hackathon-2026
pip install -r code/requirements.txt
```

**Clone it somewhere that is NOT inside OneDrive, Dropbox or iCloud.** `C:\dev\hackathon` or
`~/hackathon` is fine. Let git do the syncing.

---

## The workflow: both push to `main`, no pull requests

For two people on one day, a review gate costs more than it saves. Small commits, pushed often.

```bash
git pull --rebase        # ALWAYS before you push
# ...work...
git add -A
git commit -m "what changed"
git push
```

If `git push` is rejected, someone pushed while you were working. Run `git pull --rebase` and
push again. That is the whole protocol.

**Commit small and often.** Ten commits an hour is fine. One commit at midnight is how you lose
an afternoon.

---

## What actually prevents conflicts: own your files

Git conflicts happen when two people edit the same lines. The fix is not a better git workflow,
it is not editing the same files.

| Owner | Files |
|---|---|
| **Julie** | `docs/`, the hazard definitions and rubric wording, the write-up, the video script, anything in `research/` |
| **Paul** | `code/`, `data/`, the published site, anything that runs |
| **Either, but say so in chat first** | `HANDOVER.md`, `README.md`, `COLLABORATION.md` |

If you need a change in the other person's territory, ask rather than edit. It takes ten seconds
and saves a merge.

**Never commit `.env`.** It is gitignored. API keys stay local, and you each use your own.

---

## Can Claude Code review a change before you accept it?

Yes. In an interactive Claude Code session:

- `/code-review` — reviews the current uncommitted diff
- `/code-review <branch>` — reviews a branch
- `/code-review <PR#>` — reviews a GitHub pull request
- You can also just ask: *"review what changed in the last three commits before I push"*

**But do not gate every change through it.** On a one-day build that is pure friction. Use it
in two places where it earns its keep:

1. **Before the final submission**, over the whole diff. Catches the embarrassing thing.
2. **On the scoring logic specifically** — whatever computes the index or grades the answers.
   That is the code where a silent bug becomes a wrong finding on a slide, and it is worth one
   careful pass.

There is also a deeper multi-agent review, `/code-review ultra`, which runs in the cloud and is
billed. It is user-triggered — Claude cannot launch it for you, you have to type it. Probably
overkill for a weekend, but it exists.

---

## Keeping two Claude Code sessions in sync

Each session only knows what is in its own context. Two things help:

- **`HANDOVER.md` is the shared brain.** When you decide something that changes direction, write
  it there and push. The other session picks it up on the next `git pull`.
- **Start a session by having it read the state**: *"read HANDOVER.md and data/DATA_DICTIONARY.md
  before we start"*. Thirty seconds, and it stops you re-litigating settled decisions — section
  5 of the handover exists precisely for that.

---

## What NOT to do

- **Do not use a shared cloud drive as the collaboration mechanism.** See the top of this file.
- **Do not commit `cache/`.** It is 38MB of API responses and fully regenerable. Already ignored.
- **Do not both run `build_councils.py` at once.** It hits 78 council websites; two of you doing
  it simultaneously is rude and pointless. It is already run and the output is committed.
- **Do not force-push `main`.** If something looks broken, ask before rewriting shared history.
