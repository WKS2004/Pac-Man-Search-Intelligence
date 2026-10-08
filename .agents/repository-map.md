# Repository map

Verify current paths and implementation state before relying on this map.

| Path | Responsibility | Edit boundary |
| --- | --- | --- |
| `AGENTS.md` | Repository-wide entry and essential restrictions | User-requested instruction work |
| `.agents/` | Focused rules, routing, skills and resource checks | User-requested agent-resource work |
| `README.md` | Existing project overview at root | Read-only until a README task is authorized |
| `src/search.py` | Generic DFS, BFS, UCS and A*: Q1-Q4 | Authorized assignment implementation only |
| `src/searchAgents.py` | Agents/problems, corners and food heuristics: Q5-Q7 | Only requested assignment portions |
| `src/util.py` | Supplied fringe structures and helpers | Read-only |
| `src/pacman.py`, `src/game.py`, `src/layout.py` | Game runner, state/action/grid types, maze loader | Read-only |
| `src/autograder.py`, `src/grading.py`, `src/projectParams.py` | Test loading, score reporting and project parameters | Read-only |
| `src/searchTestClasses.py`, `src/testClasses.py`, `src/testParser.py` | Test behavior and parser | Read-only |
| `src/test_cases/` | Q1-Q8 configurations, inputs and expected solutions | Read-only; Q8 outside PDF assessed scope |
| `src/layouts/` | Supplied mazes | Read-only |
| `src/graphicsDisplay.py`, `src/graphicsUtils.py`, `src/textDisplay.py` | Graphical/text displays | Read-only |
| `src/ghostAgents.py`, `src/pacmanAgents.py`, `src/keyboardAgents.py` | Supplied agent examples and controls | Read-only |
| `src/eightpuzzle.py`, `src/VERSION` | Extra search example and starter version | Read-only |

## Persistent conventions

- The user intentionally relocated the supplied project into `src/`; do not undo it.
- Run Pac-Man/autograder commands from `src/`. Run agent-resource checks from root.
- The two allowed files form the entire code submission. Other files must not enter
  the ZIP, even if an agent-resource file contains useful implementation guidance.
- Report/evidence/package locations outside `src/` are chosen only when those
  artifacts are requested; this map does not claim any report already exists.
- Do not freeze starter status or test scores in this map. Inspect current source
  and results for each requested audit.

## Requirement lookup

Read [assignment](rules/assignment.md) for the exact local PDF source and Q1-Q7
allocation, [grading](rules/grading.md) for discrepancies,
[testing](rules/testing.md) for commands and [report-submission](rules/report-submission.md)
for deliverables.

BLUEVERSE at `D:\WKS\Projects\BLUEVERSE` was a read-only reference for resource
organization. No BLUEVERSE application rules, skills, account mappings or
dependencies govern this Python assignment.
