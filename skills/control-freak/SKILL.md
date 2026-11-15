---
name: control-freak
description: Use when about to execute or implement a multi-task implementation plan, when the user wants to review each task before it is committed, or when the user invokes control-freak by name. Also use when working in a project that has a .control-freak/QUIRKS.md file.
license: MIT
---

# Control Freak

## Overview

Implement one task, then stop. The human reviews it, you revise until they are
satisfied, and you commit only when they explicitly approve. Then the next task.

**Why:** reviewing a large implementation at the end is exhausting and too late
to change course. Reviewing one task at a time keeps each review small and lets
the human redirect the work as soon as code smells or gets hard to read.

**The human is not slowed down by the stops. The stops are the product.** A
request to "be quick" or "be efficient" means keep each task tight. It does not
mean skip reviews.

While this skill is active it overrides any other skill's or plan's instruction
to continue through tasks without stopping. Other skills still apply inside a
task (testing, debugging).

## The Loop

```
preflight -> [ implement ONE task -> verify -> STOP and report
               -> revise until approved -> commit ] -> next task
```

### 0. Preflight (once)

1. **Git.** If the directory is not a git repository, or has uncommitted
   changes, tell the human and ask how to proceed. Each task's diff must
   contain only that task.
2. **Plan.** Use the plan that exists: a plan file, another skill's output, or
   the conversation. If there is none, draft a short task list and get it
   approved.
3. **Quirks.** Read `.control-freak/QUIRKS.md` if it exists (see Quirk Memory).
4. **Tasks.** Restate the tasks as a numbered list. If a task looks too large to
   review comfortably, propose splitting it. If the plan and the task list are
   clear, go straight on to task 1. Do not stop only to ask "shall I start?".

### 1. Implement one task

- Look up the quirks for the files and folders this task touches.
- Work on the current task only. Do not start, prepare, or stub the next one.
- Do not edit outside the task's scope. Report unrelated problems instead of
  fixing them.
- You may use subagents to implement. The review stop happens in the main
  conversation, with the human.
- If the plan turns out to be wrong or unworkable, stop and say so. Do not
  improvise a different design.

### 2. Verify

Run the tests and lint relevant to the task, and wait for them to finish before
you report. Report real results, including failures and anything you could not
run.

### 3. Stop and report

End your turn with this report and nothing after it:

```markdown
## Review: Task <n> of <total>: <title>

**What changed and why:** <a few sentences>

**Files:**
- `path/to/file.ext:line` - <what>

**Checks:** <tests and lint run, with results>

**Quirks applied:** <quirks from memory that shaped this task, or "none">

**Concerns:** <anything that smells, reads badly, deviates from the plan, or
that you are unsure about, or "none">

**Proposed quirks:** <new quirk and the heading it would go under, or "none">

Nothing is committed. Review the diff, then tell me what to change, or approve
and I will commit and move on to Task <n+1>: <title>.
```

Do not print the full diff unless asked. The human reads it in their own tools.

### 4. Revise

- Apply the feedback, within the task. Re-verify. Report again in the same
  format, starting with what changed since the last report.
- Repeat as often as the human wants. Nothing is committed during revision.
- If feedback is unclear, or you believe it is technically wrong, say so and
  ask before changing code.
- If feedback affects later tasks, update the remaining task list and show it.
- If feedback will apply again beyond this task, propose a quirk.

### 5. Commit on explicit approval

| The human says | It is | You do |
|---|---|---|
| "approved", "commit", "lgtm", "ship it" | Approval | Commit this task |
| "looks good, but rename X" | A change request | Change, report, wait again |
| "ok", "hmm", a question, an unrelated remark | Not approval | Answer, then ask |
| Nothing | Not approval | Wait |

- One commit per task, containing only that task's changes (plus any quirks
  confirmed during it), with a message describing the task.
- Never push unless asked.

### 6. Next task

Say which task is next and return to step 1. After the last task, summarise the
commits made and stop.

## Hard Rules

- **No commit without explicit approval of this task.**
- **No starting the next task until the current one is committed.**
- **Approval never carries over.** "Go ahead", "implement the plan", or approval
  of an earlier task approves nothing that has not been reviewed yet.
- **No writing to the quirk memory without the human confirming the quirk.**

| Thought | Reality |
|---|---|
| "The tasks are tiny, I'll batch them" | Small tasks make small reviews. Stop after each. |
| "They are short on time" | They chose this skill. Skipping reviews moves the cost to the end, where it is larger. |
| "I'll do all the work and present it task by task" | Later tasks are then built on unreviewed code. Stop before starting the next. |
| "Task 2 depends on task 1, so I'll do both" | That is the reason to get task 1 reviewed first. |
| "They said go ahead at the start" | That started the plan. It approved no code. |
| "They approved the last three without changes" | Each task needs its own approval. |
| "I'll commit now, they can revert" | The commit is the human's decision. |
| "This feedback obviously belongs in memory" | Propose it. They confirm. |

## Quirk Memory

Each project keeps a memory of its quirks: things you need to know to work well
there and would otherwise get wrong or be corrected on again. Quirks are tied to
a position in the codebase, and you look them up by where you are working.

**File:** `.control-freak/QUIRKS.md` at the project root, committed with the
project. Each heading is the path or glob its quirks apply to:

```markdown
# Project quirks

## *
- Use pnpm, not npm. The lockfile is pnpm's and CI rejects others.

## src/api/**
- Handlers return Result, never throw. The router has no error boundary.

## src/api/users.ts
- Legacy id format, do not normalise. Mobile clients depend on it.
```

| Heading | Applies to |
|---|---|
| `## *` | The whole project |
| `## some/folder/**` | Everything under that folder |
| `## some/file.ext` | That file only |

**Lookup**

- Preflight: read the file. `## *` applies for the whole session.
- Before each task: list the files and folders the task will touch, and
  re-read every section whose heading matches any of them.
- If you are about to edit somewhere you did not expect to, check for matching
  sections first.
- A quirk is the human's standing instruction. If one conflicts with the plan,
  or seems wrong for the task, stop and ask.

**Capture**

- Propose a quirk when the human's feedback will apply again beyond this task,
  or when you discover something non-obvious yourself (for example a build step
  that only works in a certain order).
- Propose it in the review report: the exact bullet and its heading. Write it
  only after the human confirms. They may change the wording or position.
- One bullet per quirk: the rule, then the reason in a short sentence.
- Use the narrowest heading that is still correct. Order sections from general
  to specific.
- Not quirks: one-off corrections, task status, history, anything the code or a
  linter already states.
- Update an existing quirk instead of adding a duplicate. If a quirk is wrong,
  outdated, or its path is gone, propose changing or removing it.
- Create the file on the first confirmed quirk.
