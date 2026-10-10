# Pac-Man repository instructions

These instructions apply to this repository, including `src/`.

Read [.agents/routing.md](.agents/routing.md), then the universal
[change-safety](.agents/rules/change-safety.md) and
[validation](.agents/rules/validation.md) rules plus the task-specific rules.
Use [.agents/repository-map.md](.agents/repository-map.md) for paths.
Read [.agents/README.md](.agents/README.md) when changing agent resources.

For contribution and report work, use the finalized
[member responsibility record](docs/member-contributions.md) and
[report plan](docs/report-submission-plan.md), listed in the
[document index](docs/README.md). Preserve the confirmed member order and question
ownership. Carry only names, registration numbers and GitHub usernames
from member identity sources; exclude other personal or academic information.
Assigned responsibilities are not evidence of completed work.
Do not create or update AI usage records in this repository, as requested by the user.

## Non-negotiable assignment boundaries

- Current authorization covers agent resources and requested project/contribution
  documentation. Source implementation still requires an explicit user request
  or authorization.
- After implementation is authorized, the only editable assignment source files
  are the existing `src/search.py` and `src/searchAgents.py`.
- Every other file anywhere under `src/` is strictly read-only, including
  untracked files and nested directories. Agents must not create, delete, rename,
  move or generate files under `src/`, even during implementation or testing.
- All supplied framework, grader, tests, solutions, layouts and other source files
  remain read-only. Never rename supplied interfaces or alter grader expectations.
- Reject every unauthorized source change, including tool side effects. Before
  agent operations, snapshot `src/`; after each operation and before completion,
  check it. Automatically restore the agent's own violations to that snapshot
  under [the recovery procedure](.agents/rules/change-safety.md#mandatory-rejection-and-recovery).
  Preserve pre-existing and concurrent user edits; never blindly restore Git HEAD.
- Use the supplied `util.Stack`, `util.Queue` and `util.PriorityQueue` fringes.
- Assess Q1-Q7 against the PDF; Q8 is not required unless explicitly requested.
- The supplied project lives in `src/`; run its commands from that directory.
- BLUEVERSE and its `.agents` are reference-only. Do not modify them.
- Skills and registry entries guide work; they do not grant edit, Git or publication
  permission. Later explicit user instructions determine authorized task scope.
