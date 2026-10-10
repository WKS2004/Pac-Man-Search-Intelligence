# Report and submission plan

**Group:** 2026-AI-45

**Responsibility allocation:** Finalized on 10 October 2026

**Planning document:** Finalized

**Submission report status:** Q1, Q2, Q3, Q4 and Q5 each pass the supplied
grader for 3/3 provisional points; Q1 was run in Python 3.11 `cs188`, and the
supplied Q2–Q5 outputs do not identify their interpreters. Q6–Q7 implementation
remains pending, and report evidence for all question sections is incomplete.

Use [member-contributions.md](member-contributions.md) as the authoritative
identity and responsibility record. Assigned work must not be described as
completed work until it is supported by evidence.
Ushan coordinates report assembly and Adithya coordinates final verification.
Each question owner supplies their explanation and actual grading evidence;
Wanshaja coordinates food benchmark and Git evidence collection.

## Assessment

| Component | Marks | Basis |
| --- | ---: | --- |
| Q1-Q7 implementation | 40 | Group results under the detailed Pac-Man requirements |
| Group report | 10 | Structure, clarity and completeness |
| Individual Git contribution | 10 | Genuine participation, history and collaboration |
| Individual algorithm knowledge | 20 | Understanding of DFS, BFS, UCS, A* and heuristics |
| Individual code comprehension | 20 | Understanding and defense of the whole solution |
| Total | 100 | Assignment contributes 10% of the final grade |

The team viva is limited to six minutes. Every member must understand all seven
questions. The supplied PDF states no submission deadline.

## Question section ownership

| Report section | Owner | Required function or block | Evidence still needed |
| --- | --- | --- | --- |
| Q1 | Adithya | `depthFirstSearch` | Grader reports provisional 3/3 in Python 3.11 `cs188`; explanation draft appears below. Owner review, screenshot and actual contribution evidence are still needed |
| Q2 | Ushan | `breadthFirstSearch` | Supplied grader output reports provisional 3/3 across all five tests; `mediumMaze` path length 68, 269 expanded nodes. Explanation draft appears below; owner review, screenshot and actual contribution evidence are still needed. Interpreter not identified in the output |
| Q3 | Adithya | `uniformCostSearch` | Supplied grader output reports provisional 3/3 across all ten tests; `mediumMaze` path/expansion pairs are 68/269, 74/260 and 152/173, and `testSearch` is 7/14. Explanation draft appears below; owner review, screenshot and actual contribution evidence are still needed. Interpreter not identified in the output |
| Q4 | Sanuda | `aStarSearch` | Supplied `python autograder.py -q q4` output reports provisional 3/3 across all six tests; `mediumMaze` path length 68, 221 expanded nodes. Explanation draft appears below; owner review, screenshot and actual contribution evidence are still needed. Interpreter not identified in the output |
| Q5 | Ushan | `CornersProblem` start, goal and successor methods | Supplied q5 output reports the Q2 dependency and Q5 each passing for provisional 3/3; `tinyCorner` solution length 28. Explanation draft appears below; owner review, screenshot and actual contribution evidence are still needed. Interpreter not identified in the output |
| Q6 | Sanuda | `cornersHeuristic` | Actual implementation, q6 screenshot, correctness argument and expansion count |
| Q7 | Wanshaja | `foodHeuristic` | Actual implementation, q7 screenshot, correctness argument and expansion count |

Each question section must identify the edited functions/code blocks, include a
clear screenshot of actual autograder output and explain the logic, data
structures and heuristic design in **at most 200 words**. Do not write invented
implementation descriptions or present performance targets as achieved results.

## Current implementation status

`src/search.py` contains a Q1 `depthFirstSearch` implementation using
`util.Stack` and a visited-state set. The supplied Q1 autograder command
`python autograder.py -q q1`, run from `src/`, passed all five tests for 3/3
local points in the assignment-recommended Python 3.11 `cs188` environment:
`graph_backtrack`, `graph_bfs_vs_dfs`, `graph_infinite`, `graph_manypaths` and
`pacman_1`. On `mediumMaze`, the grader reported a 130-step solution and 146
expanded nodes.

**Q1 explanation draft for owner review (under 200 words):** Depth-first
search puts the start state and an empty action path in the supplied
`util.Stack`. It removes the most recently added entry, so it follows one path
deeper before exploring earlier alternatives. When a goal is reached, it
returns the actions stored with that state. A visited-state set prevents the
algorithm from expanding the same state repeatedly; each newly expanded state
adds its unvisited successors with the corresponding action appended. If the
stack empties without finding a goal, it returns an empty path. Because this
search follows depth-first order, it does not guarantee the fewest-move path.

The supplied Q2 output for `python autograder.py -q q2` reports all five tests
passing for 3/3 local points: `graph_backtrack`, `graph_bfs_vs_dfs`,
`graph_infinite`, `graph_manypaths` and `pacman_1`. On `mediumMaze`, it reports
a 68-step solution and 269 expanded nodes. The output does not identify the
Python interpreter. Both scores are provisional and unregistered.

**Q2 explanation draft for owner review (under 200 words):** Breadth-first
search places the start state and an empty action path in the supplied
`util.Queue`. It removes entries in FIFO order, so paths are expanded in
nondecreasing number of moves. When a goal state is removed, its action path is
returned. The algorithm skips states already expanded, records each newly
expanded state, and queues its unvisited successors with the corresponding
action appended. When every move has equal cost, this ordering makes the first
goal path a shortest path in number of moves. The implementation does not use
`stepCost`, so it does not guarantee minimum total cost when move costs differ.
If the queue empties before a goal is found, it returns an empty path.

The supplied Q3 output for `python autograder.py -q q3` reports all ten tests
passing for 3/3 local points: `graph_backtrack`, `graph_bfs_vs_dfs`,
`graph_infinite`, `graph_manypaths`, `ucs_0_graph`, `ucs_1_problemC`,
`ucs_2_problemE`, `ucs_3_problemW`, `ucs_4_testSearch` and
`ucs_5_goalAtDequeue`. The three `mediumMaze` cases report solution lengths
and expansions of 68/269, 74/260 and 152/173; `testSearch` reports 7/14. The
output does not identify the Python interpreter. The score is provisional and
unregistered.

**Q3 explanation draft for owner review (under 200 words):** Uniform-cost
search puts the start state, an empty action path and cost zero in the supplied
`util.PriorityQueue`. Each entry is removed in order of lowest accumulated
cost. The algorithm skips states already expanded, marks a newly removed state
visited, and returns its action path if it is a goal. Otherwise, it adds each
unvisited successor's `stepCost` to the current cost, appends the successor's
action to the path, and queues the resulting entry with its cumulative cost as
priority. Assuming nonnegative step costs, the first goal removed has minimum
total path cost. If the queue empties before a goal is found, it returns an
empty path.

The supplied Q4 output for `python autograder.py -q q4` reports all six tests
passing for 3/3 local points: `astar_0`, `astar_1_graph_heuristic`,
`astar_2_manhattan`, `astar_3_goalAtDequeue`, `graph_backtrack` and
`graph_manypaths`. On `mediumMaze`, it reports a 68-step path and 221 expanded
nodes. The output does not identify the Python interpreter. The score is
provisional and unregistered.

**Q4 explanation draft for owner review (under 200 words):** A* puts the start
state, an empty action path and cost zero in the supplied `util.PriorityQueue`,
with priority `g + h`. It removes the lowest-priority entry, skips it if its
path cost is no longer the best known for that state, and returns its action
path if it is a goal. For each successor, it adds `stepCost` to `g` and queues
the successor only when the resulting cost improves the best known cost, using
the new cost plus the supplied heuristic as priority. This skips stale entries
and allows a cheaper path to reopen a state. With an admissible heuristic that
is zero at goals and nonnegative step costs, A* returns a minimum-cost path. If
the queue empties first, it returns an empty path.

The supplied output for `python autograder.py -q q5` runs dependency Q2 and Q5.
All five Q2 tests pass for 3/3, with a 68-step `mediumMaze` path and 269
expanded nodes. The Q5 `corner_tiny_corner` test passes for 3/3 with a 28-step
solution on `tinyCorner`. Both scores are provisional and unregistered. The
output does not identify the Python interpreter.

**Q5 explanation draft for owner review (under 200 words):** `CornersProblem`
represents a state as Pac-Man's position paired with a tuple of four booleans,
one per corner. The start state marks a corner visited if Pac-Man begins there.
For each legal move, the successor records the new position and updates the
tuple so visited corners stay marked and a corner at the new position becomes
visited. Each move costs one. A state is a goal when all four tuple entries are
true. This compact, hashable state lets graph search distinguish reaching the
same position with different remaining corners, while `_expanded` counts each
successor expansion as required by the supplied framework.

The Q1/Q2/Q3/Q4/Q5 output screenshots, owner review of the Q1/Q2/Q3/Q4/Q5
explanation drafts, and genuine contribution evidence remain needed for the report. This records
repository code and test status only; it does not establish which member
authored any implementation or complete that member's contribution evidence.
Q6–Q7 remain unimplemented.

## Verification and performance

Run the supplied autograder from `src/`, separately for each assessed question:

```text
python -B autograder.py -q q1 --no-graphics
python -B autograder.py -q q2 --no-graphics
python -B autograder.py -q q3 --no-graphics
python -B autograder.py -q q4 --no-graphics
python -B autograder.py -q q5 --no-graphics
python -B autograder.py -q q6 --no-graphics
python -B autograder.py -q q7 --no-graphics
```

Use Python 3.9-3.11; the assignment's Conda example uses Python 3.11 with numpy
and matplotlib. Verify graphical keyboard play separately. Read actual scores
and dependency messages; a successful process exit alone is not proof of passing.

| Question | Benchmark | Expansion band | PDF marks |
| --- | --- | --- | ---: |
| Q6 | `mediumCorners` | At most 1,200 | 8/8 |
| Q6 | `mediumCorners` | 1,201-1,600 | 6/8 |
| Q6 | `mediumCorners` | 1,601-2,000 | 4/8 |
| Q6 | `mediumCorners` | More than 2,000 | 0/8 |
| Q7 | `trickySearch` | At most 9,000 | 8/8 |
| Q7 | `trickySearch` | 9,001-12,000 | 6/8 |
| Q7 | `trickySearch` | 12,001-15,000 | 4/8 |
| Q7 | `trickySearch` | More than 15,000 | 2/8 |

Performance credit requires correct heuristics. Both heuristics must be
admissible and consistent. Q6 explicitly receives zero for an inadmissible
heuristic or a detected non-optimal result regardless of expansion count.
The unchanged local grader uses different point weights; record its output
separately from the PDF marks. Q8 is not required.

## Report ending

- [ ] Include the group repository URL:
  `https://github.com/WKS2004/Pac-Man-Search-Intelligence`.
  Check actual visibility and resolve the publication conflict below.
- [ ] Include genuine commit-history and contribution-graph screenshots covering
  each member's work throughout the assignment.
- [ ] Include the confirmed names and registration numbers from the contribution
  plan, together with specific **actual** tasks and questions completed.
- [ ] Include the AI tool names and exact prompts as required by the assignment.

This requirement belongs to the final submission report. Repository AI usage
records and prompt transcripts have been removed and must not be created or
updated, as requested by the user. This plan records the requirement without
maintaining such records.

## Final readiness checklist

- [ ] Capture the actual Q1, Q2, Q3, Q4 and Q5 autograder output screenshots.
- [ ] Have the Q1–Q5 owners review and finalize their explanation drafts in
  Current implementation status.
- [ ] Implement Q6-Q7 and verify legal paths and required optimality.
- [ ] Run the supplied autograder for Q6-Q7 and record actual results.
- [ ] Verify Q5 state representation and corner bookkeeping.
- [ ] Explain and verify Q6/Q7 admissibility, consistency, goal behavior and
  nonnegativity; record expansion counts and runtime.
- [ ] Capture actual results for all seven question sections.
- [ ] Check word limits, formatting, screenshot clarity and identity consistency.
- [ ] Reconcile final contributions with actual Git evidence.
- [ ] Complete all AI disclosures, including assistance outside this chat.
- [ ] Confirm instructor clarification where document discrepancies affect the
  decision, especially publishing completed solutions.
- [ ] Complete a timed team viva rehearsal with questions for every member.
- [ ] Verify source integrity and inspect the final ZIP contents.

The allocation and planning documents are finalized. This checklist deliberately
remains open until the underlying implementation and evidence are complete.

## Submission files

Submit once per group as two separate items:

1. `Group_2026-AI-45_Report.pdf`: the completed report as a standalone PDF.
2. `Group_2026-AI-45_Code.zip`: only `search.py` and `searchAgents.py` at the archive
   root, taken from `src/`. Exclude the `src/` wrapper and every other file.

Keep artifacts outside `src/`. The contribution plan PDF is a planning document;
it does not replace the required submission report. Do not package starter code
as a completed submission or submit artifacts merely because documentation is
ready.

## Unresolved guideline differences

The detailed Pac-Man rubric assigns 40 implementation marks, while the local
grader declares different points including Q8. The PDF heading also uses a
different module code and its final page gives a separate general rubric.
Preserve these discrepancies rather than inventing a conversion or replacing
the detailed requirements.

The PDF requests a public repository, while the supplied Berkeley notices
prohibit publishing solutions. Obtain instructor clarification before publishing
completed solution code; existing repository visibility does not resolve that
conflict.
