# Project documents

**Group:** 2026-AI-45

**Documentation finalized:** 10 October 2026

The confirmed responsibilities are Adithya Q1/Q3 (8 marks), Ushan Q2/Q5
(12 marks), Sanuda Q4/Q6 (12 marks) and Wanshaja Q7 (8 marks). The totals cover
40 group implementation marks; they are not individual grades or achieved scores.

| Document | Purpose | Status |
| --- | --- | --- |
| [Member contributions](member-contributions.md) | Verified names, registration numbers, GitHub usernames, question ownership and handoffs | Finalized responsibility plan |
| [Report and submission plan](report-submission-plan.md) | Report owners, assessment requirements, verification targets and submission checklist | Q1/Q2 local grader: provisional 3/3 each; Q2 explanation draft included, evidence pending |
| [Contribution plan PDF](../output/pdf/Group_2026-AI-45_Contribution_Plan.pdf) | Shareable copy of the responsibility plan | Finalized planning artifact |
| [Project overview](../README.md) | Setup, search examples, testing and collaboration | Q1/Q2 local grader: provisional 3/3 each; Q2 interpreter unspecified |
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
all five supplied tests for 3/3 provisional points. Q2 uses `util.Queue` to
expand shallowest paths first and finds a fewest-move path when all step costs
are equal. Q1 was run in the
assignment-recommended Python 3.11 `cs188` environment and returned a 130-step
`mediumMaze` path with 146 expanded nodes. The supplied Q2 output reports a
68-step path and 269 expanded nodes; it does not identify the interpreter. Both
scores remain unregistered. Q3–Q7 remain unimplemented. The completed
submission report and code ZIP still require Q1/Q2 output screenshots, the Q1
explanation, owner review of the Q2 explanation draft, and genuine contribution
evidence. All artifacts remain outside `src/`; further source implementation
requires its own explicit authorization.
