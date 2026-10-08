---
name: pacman-search-implementation
description: Implement or revise authorized Pac-Man Q1-Q7 search algorithms, corner states, and heuristics within the two-file assignment allowlist.
---

# pacman search implementation

Read the root [AGENTS.md](../../../AGENTS.md) and use the `search-implementation` route in
[routing.md](../../routing.md). The universal rules and that route's focused
rules remain authoritative. Load only the references needed for this task.

Complete only the source work the user has authorized.

- Confirm source implementation authorization from the conversation. Selecting
  this skill or a routing profile is not authorization.
- Inspect the relevant function and its callers/test contract. Limit edits to
  `src/search.py` and `src/searchAgents.py`, preserving supplied interfaces.
- Use the search-algorithms rule for fringe selection, duplicate/cost handling,
  corner state representation, admissibility and consistency.
- Choose a defensible heuristic and explain why it is a lower bound and consistent.
  Benchmark its expansion count; do not promise thresholds before measuring.
- Run the relevant unchanged supplied questions from `src/`; include dependencies.
  Diagnose failures inside allowed code without altering tests or the framework.
- Review changed-file scope and protected-file integrity before reporting the
  implementation, results and remaining report/evidence work.
- Do not implement Q8, commit, publish or package unless the requested scope
  includes those actions.
