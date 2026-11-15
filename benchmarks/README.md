# Benchmarks

What does stopping for review after every task cost in tokens?

## Result

Same three-task plan, three runs without the skill and three with it. Every run
ended in the same state: three commits, all tests passing. Figures are means
per run.

| | Without skill | With control-freak | Difference |
|---|---:|---:|---:|
| Output tokens | 2,290 | 5,001 | +2,711 (2.2x) |
| Input tokens written to cache | 36,176 | 43,465 | +7,289 (1.2x) |
| Input tokens read from cache | 53,480 | 355,411 | +301,931 (6.6x) |
| Uncached input tokens | 5 | 26 | +21 |
| API calls | 2.7 | 10 | +7.3 |

Per task, the review stop costs about:

- **900 output tokens**, which is the review report;
- **2 to 3 extra API calls**, because the agent stops and is resumed. Their
  input is almost entirely the existing conversation read back from the prompt
  cache;
- nothing for the skill file after the first load. `SKILL.md` is about 7,700
  characters, roughly 2,000 tokens, and is read once per session.

## How to read this

- **The overhead is per task, not per token of work.** The tasks in this plan
  are a few lines of code each, so a 600-token review report is larger than the
  code it reports on. That is why output is 2.2x here. The benchmark did not
  measure larger tasks. The per-task figures above are the numbers to carry
  over, not the ratios.
- **About 30,000 of the cached input tokens in every run are the agent's own
  system prompt and tool definitions**, with or without the skill.
- **Cache reads dominate the difference.** They are billed at a fraction of the
  normal input price, so the raw token total overstates the cost difference.
- **Three runs per condition.** Runs within a condition were within 7% of each
  other on output tokens. Baseline run 3 made one fewer API call than the other
  two, which is why its cache-read figure is lower.
- **Straight approvals only.** Every review was answered with "approved". A
  real session with revisions costs more, and that cost is the review doing its
  job.
- **Measured on Claude Code subagents running `claude-fable-5-2`**, on
  2026-11-15. OpenCode was not measured.

## Per-run data

`results.json` holds the raw totals for each run.

| Run | Output | Cache write | Cache read | API calls |
|---|---:|---:|---:|---:|
| baseline-1 | 2,298 | 36,743 | 65,153 | 3 |
| baseline-2 | 2,271 | 36,750 | 65,151 | 3 |
| baseline-3 | 2,301 | 35,036 | 30,136 | 2 |
| skill-1 | 4,793 | 43,319 | 354,795 | 10 |
| skill-2 | 5,104 | 43,558 | 355,645 | 10 |
| skill-3 | 5,106 | 43,518 | 355,793 | 10 |

## Reproduce

1. Copy `fixture/` to a new folder for each run, add empty
   `textkit/__init__.py` and `tests/__init__.py`, and commit it as a new git
   repository.
2. Start one agent per run with the prompts in `prompts.md`. For the skill
   runs, reply "approved" at each review stop.
3. Sum the usage from each agent's transcript:

   ```bash
   python3 measure.py baseline-1=path/to/transcript.jsonl skill-1=path/to/other.jsonl
   ```

`measure.py` reads the `usage` object of every assistant response in a Claude
Code JSONL transcript and de-duplicates responses by message id.
