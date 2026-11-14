# control-freak skill: design

Date: 2026-11-14

## Purpose

`control-freak` is an agent skill for Claude Code and OpenCode. It governs how
an implementation plan is executed: the agent implements one task, stops for
human review, revises until the human is satisfied, and commits only on explicit
approval before starting the next task.

It exists to:

- spread review across the work, instead of one exhausting review at the end of
  a large implementation;
- allow course correction while it is cheap, when an implementation shows code
  smells or is hard to read.

Success means: the human has read and approved every commit, the agent never
commits or advances without permission, and the human can redirect the work at
any task boundary.

## Scope

In scope: execution of an existing plan, the review stop, the revision loop, the
commit gate, the per-project quirk memory, and installation for both tools.

Out of scope (deliberately):

- Writing plans. The skill uses whatever plan exists.
- Enforcement hooks that block `git commit`. Hooks differ between the two tools.
  Add one later only if the agent is seen ignoring the gate.
- Custom slash commands such as `/approve`. A plain reply is enough.

## Files

| Path | Role |
|---|---|
| `control-freak/SKILL.md` | The skill. Single source, loaded natively by both tools. |
| `README.md` | What the skill does and how to install it. |
| `~/.config/opencode/skills/control-freak` | Symlink to `control-freak/` in this repo. |
| `~/.claude-personal/skills/control-freak` | Symlink to `control-freak/` in this repo. |

The repo lives at `/home/ibrahim/ControllFreak` and is a git repository.

`SKILL.md` frontmatter has `name: control-freak` and a `description` that says
when to use it. The body avoids tool names specific to one harness (it says
"ask the human" and "run the tests", not the name of a particular tool), so the
same file works in both.

## Trigger

The skill applies when the agent is about to execute an implementation plan with
more than one task, or when the human invokes it by name.

While active, it overrides any other execution skill's instruction to continue
through tasks without stopping. Other skills still apply inside a task (for
example test-driven development or debugging).

## The loop

### 0. Preflight (once)

- Check that the working directory is a git repository. If not, tell the human
  and ask whether to initialise one or proceed without commits.
- Check for uncommitted changes. If the tree is dirty, tell the human and ask
  how to handle it, so that each task's diff contains only that task.
- Load the plan from wherever it is: a plan file, another skill's output, or the
  conversation. If there is no plan, draft a short task list and get approval.
- Read the project's quirk memory if it exists (see Quirk memory).
- Restate the tasks as a numbered list and confirm the boundaries.
- If a task looks too large to review comfortably, propose splitting it.

### 1. Implement one task

- Look up the quirks for the positions this task touches (see Quirk memory).
- Work on the current task only.
- Do not start the next task.
- Do not make edits outside the task's scope. Note unrelated problems in the
  review report instead of fixing them.
- Subagents may be used to implement the task. The review stop always happens in
  the main conversation.
- If the plan turns out to be wrong or unworkable, stop and report. Do not
  improvise a different design.

### 2. Verify

Run the tests and lint that are relevant to the task. Report the real results,
including failures and anything that could not be run.

### 3. Stop and report

End the turn with a review report containing:

- **Task:** number and title, for example "Task 3 of 7".
- **What changed and why:** a few sentences.
- **Files:** changed files with line references.
- **Checks:** test and lint results.
- **Quirks applied:** the quirks from memory that shaped this task, if any.
- **Concerns:** anything that smells, reads badly, deviates from the plan, or
  that the agent is unsure about. If there are none, say so.
- **Proposed quirks:** any new quirk the agent suggests saving, with its
  position, for the human to confirm.
- **Request:** ask for review, and state that nothing has been committed.

The human reads the actual diff in their own editor or git tool. The full diff
is not printed in chat unless the human asks.

### 4. Revise

- Apply the human's feedback, within the task.
- Re-run verification.
- Report again in the same format, saying what changed since the last report.
- Repeat as many times as the human wants. Nothing is committed during revision.
- If feedback is unclear or the agent believes it is technically wrong, say so
  and ask before changing code.
- If feedback changes later tasks, update the remaining task list and show it.

### 5. Commit on explicit approval

- Commit only when the human clearly approves: "approved", "commit", "lgtm",
  "ship it", or similar.
- A reply that mixes approval with a request ("looks ok, but rename X") is not
  approval. Make the change, report, and wait again.
- A reply that is ambiguous is not approval. Ask.
- One commit per task, containing only that task's changes, with a message that
  describes the task.
- Never push unless asked.

### 6. Next task

Announce the next task and return to step 1. Approval never carries over: each
task needs its own.

After the last task, give a short summary of the commits made and stop.

## Quirk memory

Each project has a memory of its quirks: things the agent needs to know to work
well in that project and would otherwise get wrong or be corrected on
repeatedly. Quirks are positional. Each one is tied to the part of the codebase
it applies to, and the agent looks up the quirks for the position it is working
in.

### Storage

One file per project, committed with the project:
`.control-freak/QUIRKS.md`.

Each section heading is the path or glob the quirks under it apply to, relative
to the project root:

```markdown
# Project quirks

## *
- Use pnpm, not npm. The lockfile is pnpm's and CI rejects others.

## src/api/**
- Handlers return Result, never throw. The router has no error boundary.

## src/api/users.ts
- Legacy id format, do not normalise. Mobile clients depend on it.
```

Format rules:

- `## *` holds quirks that apply everywhere.
- A heading ending in `/**` applies to everything under that folder.
- A heading that is a file path applies to that file only.
- Each quirk is one bullet: the rule, then the reason in a short sentence. The
  reason lets the agent judge edge cases and lets a human spot a stale quirk.
- Sections are ordered from general to specific.
- Only quirks go here: things not obvious from reading the code. No task
  status, no history, nothing a linter or the code already states.

### Lookup

- In preflight, read the file if it exists and apply the `## *` section for the
  whole session.
- Before implementing each task, work out which files and folders the task will
  touch, and re-read every section whose heading matches any of them. A section
  matches when the path is the heading's file, or lies under the heading's
  folder.
- If the task turns out to touch a position that was not expected, check for
  matching sections before editing there.
- The review report lists the quirks that were applied, so the human can see
  the memory is being used.
- A quirk is the human's standing instruction. If a quirk conflicts with the
  plan or seems wrong for the task, stop and ask. Do not silently override it.

### Capture

- Quirks come mainly from review feedback. When the human corrects something
  that will apply again beyond the current task, the agent proposes a quirk:
  the exact bullet and the heading it would go under.
- The agent may also propose a quirk it discovered itself while working, for
  example a build step that fails unless run in a certain order.
- Nothing is written to the memory without the human confirming it. The human
  may change the wording or the position.
- Choose the narrowest position that is still correct. A quirk about one file
  goes under that file, not under `*`.
- A one-off correction that applies only to the current task is not a quirk.
- Confirmed quirks are written to the file and included in that task's commit.
- If the file does not exist, create it on the first confirmed quirk.

### Maintenance

- Before adding, check for an existing quirk that covers it, and update that
  one instead of adding a duplicate.
- If a quirk is found to be wrong or outdated, or its path no longer exists,
  propose changing or removing it at the next review stop.

## Rules the skill must state strongly

These are the places an agent is most likely to rationalise its way past the
gate, so the skill states them as hard rules with the reasoning:

- No commit without explicit approval of this task.
- No starting the next task before the current one is committed.
- No batching tasks "because they are small".
- Earlier approval, or a general "go ahead" at the start, does not approve later
  tasks.
- Silence or an unrelated reply is not approval.
- No writing to the quirk memory without the human confirming the quirk.

## Testing

Run the skill with a subagent against a small throwaway plan (three trivial
tasks in a scratch git repo) and check:

1. It stops after task 1 with a report in the specified format.
2. It has made no commit at that point.
3. Given "looks ok but rename the function", it revises and stops again without
   committing.
4. Given "approved", it makes exactly one commit and announces task 2.
5. With a `.control-freak/QUIRKS.md` holding a quirk for one folder, a task in
   that folder follows the quirk and lists it in the report, and a task
   elsewhere does not list it.
6. Given feedback that will clearly recur ("we always use X here"), it proposes
   a quirk with a position, and writes nothing until confirmed.
7. Without the skill, the same prompt runs through all tasks (baseline, to
   confirm the skill is what changes the behaviour).

Fix the skill's wording for any check that fails, and re-run.
