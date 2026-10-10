# Finalized member responsibilities

**Project:** Pac-Man Search Intelligence  
**Group:** 2026-AI-45  
**Allocation finalized:** 10 October 2026

This is the team's confirmed assignment of responsibilities. It is not a claim
that implementation, verification or submission has been completed. The final
report must describe actual contributions supported by Git and grading evidence.

## Member identities and ownership

Member numbering is specific to this Pac-Man project and follows the user's
confirmed order; it is not inherited from OCEAVERA.

| Member | Name used by the team | Name in the initial submission | Registration number | GitHub username | Questions | Marks covered |
| --- | --- | --- | --- | --- | --- | ---: |
| 1 | Adithya Gunawardana | Gunawardana M.A.A. | IT24103038 | [AdithyaGunawardana](https://github.com/AdithyaGunawardana) | Q1, Q3 | 8 |
| 2 | Ushan Srinuka | Srinuka D.G.U. | IT24100184 | [Ushan-Srinuka](https://github.com/Ushan-Srinuka) | Q2, Q5 | 12 |
| 3 | Sanuda Abeysinghe | Abeysinghe S.D. | IT24100788 | [sanudaabey](https://github.com/sanudaabey) | Q4, Q6 | 12 |
| 4 | Wanshaja Sooriyabandara | Sooriyabandara U.R.G.W.K. | IT24102798 | [WKS2004](https://github.com/WKS2004) | Q7 | 8 |
| Total | | | | | Q1-Q7 | 40 |

The 8/12/12/8 allocation covers the PDF's group implementation marks. It does not
assign individual grades or guarantee any question's score. Difficulty ratings
below are planning estimates, not lecturer-issued categories.

## Question responsibilities

| Question | Owner | PDF marks | Relative difficulty | Required implementation | Completion evidence |
| --- | --- | ---: | --- | --- | --- |
| Q1: DFS | Adithya | 4 | Low-Moderate | `search.py`: `depthFirstSearch`; graph search with `util.Stack`, expanded-state tracking and legal action paths | Supplied q1 results and explanation of cycle handling and DFS path behavior |
| Q2: BFS | Ushan | 4 | Low-Moderate | `search.py`: `breadthFirstSearch`; graph search with `util.Queue` and correct state/path handling | Supplied q2 results and shortest-path reasoning for equal step costs |
| Q3: UCS | Adithya | 4 | Moderate | `search.py`: `uniformCostSearch`; `util.PriorityQueue` ordered by accumulated cost, cheaper-path handling and stale-entry control | Supplied q3 results, varying-cost behavior and optimality reasoning |
| Q4: A* | Sanuda | 4 | Moderate-High | `search.py`: `aStarSearch`; `util.PriorityQueue` ordered by `g + h`, heuristic argument and cost bookkeeping | Supplied q4 results; comparison with UCS when the heuristic is zero |
| Q5: CornersProblem | Ushan | 8 | Moderate-High | `searchAgents.py`: `getStartState`, `isGoalState`, `getSuccessors` and corner bookkeeping; small hashable states | Supplied q5 results using BFS; start-at-corner, wall and visitation checks |
| Q6: Corners heuristic | Sanuda | 8 | High | `searchAgents.py`: `cornersHeuristic`; nonnegative, admissible, consistent and zero at goals | Supplied q6 results, correctness argument and at most 1,200 expansions on `mediumCorners` for the PDF full-credit target |
| Q7: Food heuristic | Wanshaja | 8 | High-Very High | `searchAgents.py`: `foodHeuristic`; admissible and consistent; preserve supplied `FoodSearchProblem`; caching where useful | Supplied q7 results, correctness argument and at most 9,000 expansions on `trickySearch` for the PDF full-credit target |

All questions require correct behavior, not just the listed demonstration or
node count. Local autograder points differ from the PDF marks. Q8 is outside
the required scope.

## Why this allocation was chosen

- Ushan owns Q2 and Q5 because the corner problem is verified with BFS.
- Sanuda owns Q4 and Q6 because A* directly uses the corner heuristic.
- Wanshaja owns Q7 separately to allow dedicated time for the larger food search
  space, heuristic correctness and performance tuning.
- Adithya owns two generic searches and coordinates final integration and
  verification to balance the lighter expected implementation workload.

## Shared work and supporting owners

| Responsibility | Coordinator | Contribution expected from everyone |
| --- | --- | --- |
| Integration and final Q1-Q7 verification | Adithya | Provide tested changes; investigate failures in owned questions |
| Report assembly and formatting | Ushan | Write owned question sections, at most 200 words each, with actual grading screenshots |
| A* integration and corner-heuristic defense | Sanuda | Understand `g`, `h`, priority ordering, optimality, admissibility and consistency |
| Food performance evidence and Git evidence collection | Wanshaja | Supply actual benchmark results and genuine evidence of each member's own work |
| Individual viva preparation | Every member | Understand and explain all Q1-Q7, including other members' code |

Coordinating evidence does not authorize committing as another member,
manufacturing participation, changing tests or publishing solution code.
Repository AI usage records are not created or updated, as requested by the user.
The assignment's final-report disclosure requirement is recorded in the report plan.

## Dependencies and handoffs

1. Agree on the existing search interface and legal action-path return format.
2. Ushan specifies the corner-state format before Sanuda implements Q6. Include
   the position, immutable visited-corner information and start-at-corner behavior.
3. Adithya and Sanuda review UCS/A* cost bookkeeping together. UCS provides a
   useful comparison for A* with the zero heuristic.
4. Sanuda supplies working A* for Wanshaja's food-search integration. Wanshaja
   can design the heuristic before that integration is available.
5. Each owner verifies their questions and provides evidence. Adithya then
   coordinates the complete Q1-Q7 check; Ushan assembles the report.
6. Every member explains their implementation to the other three before the viva.

Suggested review pairs are Adithya/Sanuda for UCS and A*, Ushan/Sanuda for corner
states and Q6, and Wanshaja/Sanuda for Q7 integration. Reviews supplement each
owner's responsibility rather than changing it.

## Git and source boundaries

- Use meaningful commits under the actual contributor's own identity. Record
  work throughout the assignment; do not fabricate history or equalize commit
  counts artificially.
- Suggested lowercase branch names are `feature/adithya-q1-q3`,
  `feature/ushan-q2-q5`, `feature/sanuda-q4-q6` and `feature/wanshaja-q7`.
  These are suggestions, not branches already created.
- The existing `src/search.py` and `src/searchAgents.py` are the entire editable
  assignment source boundary. Preserve all supplied interfaces and notices.
- All other files under `src/` remain read-only. Do not generate files there.
  Run Python with `-B` and keep evidence outside `src/`.
- The allocation authorizes planning, not agent source implementation, commits,
  pushes or publication. Follow the user's actual authorization for those actions.

## Identity provenance and permitted fields

The registration numbers and formal name spellings were checked against the
member tables on pages 1 and 2 of
`2026-AI-45-Machine_Learning-Initial_Submission.pdf` in the OCEAVERA initial
submission directory. The GitHub usernames were cross-checked against OCEAVERA's
`docs/project/ai-team-members.md` and this repository's contributor list; the
initial PDF contains no GitHub account links.

Only member names, registration numbers and GitHub usernames are carried into
this project's identity records. No other personal or academic information from
OCEAVERA is included. OCEAVERA's tasks and member numbering do not govern this
project.

See [the document index](README.md) and
[the report and submission plan](report-submission-plan.md). The shareable copy is
[the contribution plan PDF](../output/pdf/Group_2026-AI-45_Contribution_Plan.pdf).
