# Assignment scope and source of truth

## Assessed scope: Q1-Q7

| Question | Implementation location | PDF marks |
| --- | --- | ---: |
| Q1 | `src/search.py`: `depthFirstSearch` | 4 |
| Q2 | `src/search.py`: `breadthFirstSearch` | 4 |
| Q3 | `src/search.py`: `uniformCostSearch` | 4 |
| Q4 | `src/search.py`: `aStarSearch` | 4 |
| Q5 | `src/searchAgents.py`: `CornersProblem` | 8 |
| Q6 | `src/searchAgents.py`: `cornersHeuristic` | 8 |
| Q7 | `src/searchAgents.py`: `foodHeuristic` | 8 |

- Q8 and its closest-dot methods exist in the supplied starter, but are outside
  the PDF's assessed scope. Do not implement Q8 unless the user requests it.
- Q5 requires `getStartState`, `isGoalState`, `getSuccessors`, and corner
  successor bookkeeping. Use a small, hashable state representing position and
  corner visitation; do not include the wall grid or the full `GameState`.
- Preserve the supplied `FoodSearchProblem` representation and implementation.
- Preserve `_expanded` bookkeeping explicitly marked `DO NOT CHANGE`.

## Guidelines source

The reviewed source is the 11-page PDF at:

```text
D:\SLIIT\Y3S1\Modules\IT3012 - Intelligent Agents\Project\Project Guidelines\IT3012_2026_7_3_ IT3012 - Group Assignment (10%) _ CourseWeb.pdf
```

Read the source again if the user supplies revised guidelines. Keep inferred
engineering safeguards distinct from explicit assignment requirements.

## Requirement provenance

The PDF's requirements govern assessed work; local workflow conventions explain
how agents preserve those requirements. Hash comparisons, resource registries,
routing fixtures and artifact placement are local safeguards, not extra marks
or deliverables demanded by the lecturer.

Read [grading.md](grading.md) for document/grader discrepancies,
[report-submission.md](report-submission.md) for deliverables, and
[git-ai-usage.md](git-ai-usage.md) for collaboration and AI evidence.
