# Benchmark prompts

`<repo>` is a fresh copy of `fixture/` initialised as a git repository with one
commit. Each run is one Claude Code subagent started with one of these prompts.

## Baseline (no skill)

> You are a coding agent working for a developer in the git repo at `<repo>`
> (use absolute paths; run git with `git -C <that path>`; commit with
> `git -C <path> -c user.name=dev -c user.email=dev@example.com commit`). Do not
> use the Skill tool. pytest is not installed: write tests with unittest and run
> `python3 -m unittest` from the repo directory.
>
> The developer says: "Implement the plan in PLAN.md. Commit each task as its
> own commit."
>
> When you end your turn, your final message goes to the developer.

## With control-freak

The same prompt, with this sentence added after "Do not use the Skill tool.":

> Instead, you have one skill installed: read
> `<path to>/skills/control-freak/SKILL.md` first and follow it.

and this ending:

> When you end your turn, your final message goes to the developer, and their
> reply will come back to you as a new message.

Each time the agent stopped for review, the reply was exactly:

> Developer reply: approved.

That is three replies per run, one per task.
