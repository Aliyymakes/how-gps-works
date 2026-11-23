# Directives

Standing rules for every session. Written by the orchestrator, approved by Icarus.

## Priority order for calls the spec does not settle
Taken from the judging criteria in the brief. Approved by Icarus 2026-11-22 15:53 (his-words.md).

1. The mechanism is correct.
2. A first-time user understands the main idea within two minutes, with nobody from the team present.
3. Every teammate can explain the code they merged.
4. Depth beyond the main idea.
5. Polish.

## Never touch
- 2026-11-22 | none recorded yet. Icarus adds his own folders and files here.

## Approved
- 2026-11-22 | Pyodide (Python in the browser) and numpy, chosen by Icarus. Nothing else is approved: publishing, account use, uploads and other dependencies each need his yes.

## Away rules
If Icarus or your human is not around: decide technical calls by the priority order above and mark the decisions.md line `provisional`. Do not make taste calls; list them under "Questions for Icarus" in the pull request with a recommendation each. Stop before anything destructive or irreversible.

## Hard checks
- 2026-11-22 | The live link must work with no sign-in, no download and no API key (brief rule 3).
- 2026-11-22 | A first-time user must be able to change an input and see the output change (brief rule 2).
- 2026-11-23 | Feature freeze 25 Nov 18:59 WIB. After it, no new features: only bug fixes, the project page, the demo video and interview practice. A goal for a new feature opened after the freeze is refused.
- 2026-11-23 | user | A finished product comes before each teammate writing their own part. Any agent may build any open goal that has no pull request after its claim has sat for a few hours; the original owner reviews and learns it for the interview instead (Icarus, 21:14).
- 2026-11-23 | user | Model ladder for subagents: Fable for the hardest decisions and tasks, Opus for hard work (maths review, tricky debugging), Sonnet for regular work (code, tests, drafts), Haiku for easy work (running tests, checklists, small fixes). Use the cheapest that can do the piece well.
