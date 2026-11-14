# control-freak

An agent skill for Claude Code and OpenCode that keeps you in control of a
multi-task implementation.

The agent implements one task from the plan, then stops and reports. You review
the change and ask for revisions as many times as you like. Nothing is committed
until you explicitly approve, and only then does the agent start the next task.

This spreads review across the work instead of leaving one large review for the
end, and lets you change course as soon as the code starts to smell or gets hard
to read.

## Quirk memory

Each project can hold a memory of its quirks in `.control-freak/QUIRKS.md`.
Every section is headed by the path or glob it applies to, and the agent reads
the sections that match the files it is about to work on:

```markdown
# Project quirks

## *
- Use pnpm, not npm. The lockfile is pnpm's and CI rejects others.

## src/api/**
- Handlers return Result, never throw. The router has no error boundary.
```

When your review feedback looks like it will apply again, the agent proposes a
quirk. It is written to the file only after you confirm it. You can also edit
the file by hand.

## Install

The skill is the `control-freak/` folder. Symlink it into each tool's skills
directory:

```bash
git clone <this repo> ~/control-freak

# OpenCode
ln -s ~/control-freak/control-freak ~/.config/opencode/skills/control-freak

# Claude Code (use the skills folder of your Claude config directory)
ln -s ~/control-freak/control-freak ~/.claude/skills/control-freak
```

To install it for a single project instead, link or copy the folder into that
project's `.opencode/skills/` or `.claude/skills/`.

## Use

Have a plan (a plan file, or a task list in the conversation), then ask the
agent to implement it with control-freak. At each stop, reply with changes, or
with "approved" to commit and move on.

The design is documented in
`docs/superpowers/specs/2026-11-14-control-freak-design.md`.
