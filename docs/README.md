# Project documents

**Group:** 2026-AI-45

**Documentation finalized:** 11 October 2026

The confirmed responsibilities are Adithya Q1/Q3 (8 marks), Ushan Q2/Q5
(12 marks), Sanuda Q4/Q6 (12 marks) and Wanshaja Q7 (8 marks). The totals cover
40 group implementation marks; they are not individual grades or achieved scores.

| Document | Purpose | Status |
| --- | --- | --- |
| [Member contributions](member-contributions.md) | Verified names, registration numbers, GitHub usernames, question ownership and handoffs | Finalized responsibility plan |
| [Report and submission plan](report-submission-plan.md) | Report owners, assessment requirements, verification targets and submission checklist | Q1–Q5 local grader: provisional 3/3 each; Q1–Q5 explanation drafts included, evidence pending |
| [Contribution plan PDF](../output/pdf/Group_2026-AI-45_Contribution_Plan.pdf) | Shareable copy of the responsibility plan | Finalized planning artifact |
| [Project overview](../README.md) | Setup, search examples, testing and collaboration | Q1–Q5 local grader: provisional 3/3 each; Q2–Q5 interpreters unspecified |
| [Contributor and license information](../LICENSE.md) | Confirmed member order and existing license/attribution terms | Aligned with the confirmed team |
| [Agent instructions](../AGENTS.md) | Documentation scope, source boundaries and member-data restrictions | Applies to work throughout the repository |
| [Automation guide](../.github/AUTOMATION.md) | Existing workflows and evidence collection behavior | References the confirmed responsibility plan |

Adithya coordinates integration and verification; Ushan coordinates report
assembly; Sanuda coordinates A*/corner-heuristic integration; Wanshaja coordinates
food performance and Git evidence. Each member supplies their own question
explanations and actual results and learns the full solution for the viva.

Repository AI usage records have been removed and must not be created or updated.
The report plan still records the lecturer's disclosure requirement as an
assignment requirement; it contains no usage log or prompt transcript.

The current checkout's Q1 and Q2 implementations in `src/search.py` each pass
all five supplied tests, Q3 passes all ten, Q4 passes all six, and Q5 passes its
`corner_tiny_corner` test; each reports 3/3 provisional points. Q1 uses
`util.Stack` and a visited-state set to follow the
latest-added path first, so it does not guarantee a fewest-move solution. Q2
uses `util.Queue` to expand shallowest paths first and finds a fewest-move path
when all step costs are equal. Q3 uses `util.PriorityQueue` ordered by
accumulated cost to find a minimum-total-cost path when step costs are
nonnegative. Q1 was run in the assignment-recommended Python 3.11 `cs188`
environment and returned a 130-step `mediumMaze` path with 146 expanded nodes.
The supplied Q2 output reports a 68-step path and 269 expanded nodes; Q3 reports
`mediumMaze` paths of 68, 74 and 152 steps with 269, 260 and 173 expanded nodes,
and a 7-step `testSearch` path with 14 expanded nodes. Q4 uses `util.PriorityQueue`
with `g + h` priorities and reports a 68-step `mediumMaze` path with 221
expanded nodes. Q5 represents state as Pac-Man's position and a tuple of
visited corners, and its `tinyCorner` test reports a 28-step solution. The Q5
run also passes its Q2 dependency, which reports a 68-step `mediumMaze` path
with 269 expanded nodes. The supplied Q2–Q5 outputs do not identify their
interpreters. All five scores remain unregistered. Q6–Q7 remain unimplemented.
The completed submission report and code ZIP still require Q1–Q5 output
screenshots, owner review of the Q1–Q5 explanation drafts, and genuine
contribution evidence. All artifacts remain
outside `src/`; further source implementation requires its own explicit
authorization.
