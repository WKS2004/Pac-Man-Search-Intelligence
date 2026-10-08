---
name: pacman-search-verification
description: Run and interpret unchanged Pac-Man autograder questions, heuristic checks, and performance measurements with read-only file handling.
---

# pacman search verification

Read the root [AGENTS.md](../../../AGENTS.md) and use the `search-verification` route in
[routing.md](../../routing.md). The universal rules and that route's focused
rules remain authoritative. Load only the references needed for this task.

Establish what the current code actually passes.

- Identify the questions and dependencies needed to answer the user.
- Inspect risky execution paths before running; disable bytecode writes and avoid
  solution generation, grade-output flags, recording and frame exports.
- Run the per-question commands in the testing rule from `src/` using an identified
  interpreter. Read score/messages even if the command exits with code zero.
- Check path legality/optimality and heuristic properties where relevant. Record
  expansion counts before extra probes can increment problem bookkeeping.
- Distinguish local point totals from PDF marks, Q8 from assessed scope, and
  actual failures from dependency skips or unavailable GUI/environment checks.
- Do not fix source or change tests as part of a verification-only request.
- Provide actual results and practical limits; never fabricate screenshot evidence.
