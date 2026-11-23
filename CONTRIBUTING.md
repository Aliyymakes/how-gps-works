# How we work (read this once, it takes 5 minutes)

Four people, each with their own AI agent. This page is for the humans. The agents read `AGENTS.md`.

## Set up once

1. Install git and the GitHub command line tool (`gh`), then run `gh auth login`.
2. Clone the repo and open the folder in your agent (Claude Code, Codex or Antigravity).
3. Python people: `pip install -r requirements-dev.txt`, then `python -m pytest -q` should pass.

## The loop for every piece of work

1. Open the project board. Pick an issue from "To do" in your area. Assign it to yourself. Assigning is the lock: if it has a name on it, it is taken.
2. Start a fresh agent session in the repo folder and paste these two lines, one after the other (wait for the reply after the first):

   ```
   Read .memory/start.md and follow it.
   ```
   ```
   Do issue #NN (run: gh issue view NN). Work on a branch named NN-short-name, open a pull request that closes the issue, then stop.
   ```

3. When the agent opens the pull request, read it yourself. You must be able to explain the "Explain it" part out loud. If you cannot, ask your agent until you can. Judges will interview us on our own code.
4. Ask a teammate who did not write it to review. They (or their agent) check it against the issue's "Done when" list. The author does not approve their own work.
5. Merge. The tests run on their own and the live site updates from `main`.

## Found a bug?

Open an issue with the "Bug" template. Write what you did, what you expected and what happened, with a number if there is one ("position is 40 km off" beats "position looks wrong"). Add the browser and device. Do not fix it inside another issue's branch.

## Want to change the plan?

Do not edit `.memory/design.md`. Open an issue with the label `needs-icarus` and say what you want changed and why. Icarus decides and updates the spec.

## Rules

- Never push to `main`. One branch per issue. One agent session per issue.
- Do not let two agents work in the same folder copy at the same time.
- `docs/interface.md` is the contract between the Python side and the page. Changing it needs its own issue, and both sides agree first.
- Stage files by name (`git add path/to/file`). Never `git add .`.
- If you are stuck for more than 30 minutes, write it on the issue and tell the group.

## Who owns what

| Area | Folder | People |
|---|---|---|
| Mechanism (Python) | `mechanism/`, `tests/` | tw-2866, scoobertfan |
| Page (HTML/CSS/JS) | `index.html`, `web/` | jstnstyad10, aliyymakes |
| Spec, board, final calls | `.memory/` spec files | Icarus |
| Project page, demo video | TBA | TBA |
