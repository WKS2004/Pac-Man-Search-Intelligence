# Task routing

Read root [AGENTS.md](../AGENTS.md), then always load
[change-safety](rules/change-safety.md) and [validation](rules/validation.md).
Select the smallest applicable row. Load its workflow skill when it matches the
request; a selected skill never grants permission.

| Route | Task | Focused rules | Workflow skill |
| --- | --- | --- | --- |
| `assignment-audit` | Analyze requirements, repository readiness or gaps | [assignment](rules/assignment.md), [grading](rules/grading.md), [testing](rules/testing.md), [Git/AI](rules/git-ai-usage.md) | [pacman-assignment-audit](skills/pacman-assignment-audit/SKILL.md) |
| `search-implementation` | Authorized Q1-Q7 implementation in the two allowed files | [assignment](rules/assignment.md), [search](rules/search-algorithms.md), [testing](rules/testing.md), [grading](rules/grading.md), [Git/AI](rules/git-ai-usage.md) | [pacman-search-implementation](skills/pacman-search-implementation/SKILL.md) |
| `search-verification` | Run tests, review heuristics or measure expansions | [testing](rules/testing.md), [search](rules/search-algorithms.md), [grading](rules/grading.md) | [pacman-search-verification](skills/pacman-search-verification/SKILL.md) |
| `report-submission` | Requested report, evidence review or local ZIP | [assignment](rules/assignment.md), [report](rules/report-submission.md), [grading](rules/grading.md), [Git/AI](rules/git-ai-usage.md) | [pacman-report-submission](skills/pacman-report-submission/SKILL.md) |
| `git-collaboration` | Contribution evidence, authorized Git operations | [Git/AI](rules/git-ai-usage.md), [report](rules/report-submission.md) | No dedicated skill |
| `agent-resources` | Explicitly requested `.agents/**` or root instruction changes | [assignment](rules/assignment.md); also [resource guide](README.md) | No dedicated skill |
| `protected-framework` | A defect or requested change in supplied framework/tests/layouts | [assignment](rules/assignment.md), [testing](rules/testing.md), [grading](rules/grading.md) | Diagnose read-only; report the protected-file boundary |

For mixed requests combine relevant rows; do not treat verification as permission
to implement, or implementation as permission to publish. For an unfamiliar task,
apply universal rules first and determine the actual scope before choosing a skill.
An explicit later user instruction can update authorization; local resources must
not silently reinterpret it as permission to change assignment requirements.

The [registry](registry/skills.json) records these route IDs, rules and skills.
[Routing fixtures](evals/routing-cases.json) check representative assignments and
source-edit gates. They validate declared routing profiles, not automatic
natural-language classification. Run the [validator](scripts/validate_agent_resources.py)
after changing routing or registry metadata.
