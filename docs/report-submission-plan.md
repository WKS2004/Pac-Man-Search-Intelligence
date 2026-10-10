# Report and submission plan

**Group:** 2026-AI-45

**Responsibility allocation:** Finalized on 10 October 2026

**Planning document:** Finalized

**Submission report status:** Awaiting implementation and genuine evidence

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
| Q1 | Adithya | `depthFirstSearch` | Actual implementation, q1 screenshot and explanation |
| Q2 | Ushan | `breadthFirstSearch` | Actual implementation, q2 screenshot and explanation |
| Q3 | Adithya | `uniformCostSearch` | Actual implementation, q3 screenshot and explanation |
| Q4 | Sanuda | `aStarSearch` | Actual implementation, q4 screenshot and explanation |
| Q5 | Ushan | `CornersProblem` start, goal and successor methods | Actual implementation, q5 screenshot and explanation |
| Q6 | Sanuda | `cornersHeuristic` | Actual implementation, q6 screenshot, correctness argument and expansion count |
| Q7 | Wanshaja | `foodHeuristic` | Actual implementation, q7 screenshot, correctness argument and expansion count |

Each question section must identify the edited functions/code blocks, include a
clear screenshot of actual autograder output and explain the logic, data
structures and heuristic design in **at most 200 words**. Do not write invented
implementation descriptions or present performance targets as achieved results.

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

- [ ] Implement Q1-Q7 and verify legal paths and required optimality.
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
