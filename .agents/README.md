# Pac-Man agent resources

This directory adapts BLUEVERSE's focused resource organization to this assignment:
a root entry point, task routing, repository map, rules, local workflow skills,
registry and read-only resource validation. The guidance is authored for Pac-Man;
BLUEVERSE is reference-only and is not a runtime dependency.

## Use

1. Read root [AGENTS.md](../AGENTS.md).
2. Read [routing.md](routing.md) and the universal safety/validation rules.
3. Load only the selected task's rules and workflow skill.
4. Inspect current source/evidence; instructions never count as implementation.
5. Apply the existing user authorization and report actual verification.

[AGENTS.md](AGENTS.md) remains a compatibility pointer for earlier references.
It no longer contains the full policy. All original assignment restrictions are
maintained in the focused rules.

## Resource map

```text
.agents/
  AGENTS.md
  README.md
  routing.md
  repository-map.md
  rules/
    change-safety.md
    assignment.md
    search-algorithms.md
    testing.md
    grading.md
    report-submission.md
    git-ai-usage.md
    validation.md
  skills/
    pacman-assignment-audit/SKILL.md
    pacman-search-implementation/SKILL.md
    pacman-search-verification/SKILL.md
    pacman-report-submission/SKILL.md
  registry/
    skills.json
  evals/
    routing-cases.json
    test_source_guard.py
  scripts/
    validate_agent_resources.py
    source_guard.py
```

## Maintenance

Change agent resources only when requested. Keep the [registry](registry/skills.json),
[routing](routing.md), [fixtures](evals/routing-cases.json) and linked resources
consistent. Skills have concise discovery frontmatter and reuse the shared rules.
The four skills are local, project-authored workflows; no third-party skills are
vendored. Overlays and third-party notices are unnecessary until an actual import
requires them.

From the repository root run:

```text
python -B .agents/scripts/validate_agent_resources.py
```

The [validator](scripts/validate_agent_resources.py) uses the Python standard
library and writes no files. It checks metadata, links, route references, fixture
expectations and the two-file source policy. It does not install dependencies,
run Pac-Man, modify source, grant permissions, or impose operating-system locks.

The [source guard](scripts/source_guard.py) separately snapshots the complete
source tree to temporary storage, rejects unauthorized differences, and restores
verified agent-owned violations automatically when supplied their recorded
fingerprints. Follow [the mandatory recovery procedure](rules/change-safety.md#mandatory-rejection-and-recovery)
before agent operations and after each potentially mutating operation. Unknown
or conflicting changes are preserved and reported. This is an invoked guard,
not a background watcher; every agent must perform the checks.

Recovery regression checks run only against temporary fixture trees:

```text
python -B .agents/evals/test_source_guard.py
```

When authoring skills, also run the bundled skill-creator `quick_validate.py`
when available. Preserve BLUEVERSE and all protected assignment files when
validating this repository.

The assignment requirements and agent workflow safeguards are distinguished in
[assignment.md](rules/assignment.md). Current source permission is recorded in
[change-safety.md](rules/change-safety.md); creating this resource structure does
not authorize implementation.
