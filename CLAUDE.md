# control-freak

An agent skill for Claude Code and OpenCode. The agent implements one task of a
plan, stops for human review, revises until approved, and commits only on
explicit approval. It also keeps a per-project quirk memory in
`.control-freak/QUIRKS.md`, keyed by file and folder.

## Layout

- `skills/control-freak/SKILL.md`: the skill. This is the product; everything
  else supports it.
- `.claude-plugin/`: Claude Code plugin and marketplace manifests.
- `benchmarks/`: token-cost benchmark (fixture plan, prompts, `measure.py`,
  results).
- `docs/superpowers/specs/`: the design spec. Keep it in step with the skill.

## Rules for changing the skill

- **One file, both tools.** `SKILL.md` must work unchanged in Claude Code and
  OpenCode. Do not name harness-specific tools in it; say "ask the human" or
  "run the tests".
- **The frontmatter `description` says only when to use the skill.** Do not
  summarise the workflow there, or agents follow the summary instead of reading
  the body.
- **The spelling is `control-freak`**, one "l", everywhere: skill name, folder,
  and the `.control-freak/` memory folder.
- **Keep the skill short.** It is loaded into context on every use, and the
  review report format drives the per-task token cost.
- **Do not weaken the gate.** No clause that lets the agent commit, batch
  tasks, or write a quirk without the human's explicit say.

## Testing a change

Skill wording is tested by running agents, not by reading it.

1. Copy `benchmarks/fixture/` into a scratch git repo (add empty
   `textkit/__init__.py` and `tests/__init__.py`).
2. Run a subagent on the plan with the prompts in `benchmarks/prompts.md`, once
   without the skill and once with it.
3. Check that with the skill it stops after each task, commits nothing before
   approval, treats "looks good, but..." and "ok" as not approved, proposes
   quirks without writing them, and applies quirks only in their position.
4. If the report format changed, re-run the benchmark and update
   `benchmarks/README.md` and `results.json`.

Validate the plugin manifest with `claude plugin validate .`.

## Working in this repo

- The owner reviews before committing. Commit and push only when asked.
- Installed copies are symlinks to `skills/control-freak/` in
  `~/.config/opencode/skills/` and the Claude config's `skills/` folder, so
  edits here take effect immediately in both tools.
