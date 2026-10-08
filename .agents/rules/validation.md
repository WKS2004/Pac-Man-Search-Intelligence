# Completion and evidence

Apply this rule to every task, together with [change-safety.md](change-safety.md).

## Assignment work

- Match the completed change to the authorized scope and two-file source allowlist.
- Verify that no file was added, deleted, renamed or moved under `src/`, and
  that contents changed only in the two existing allowed files when implementation
  was authorized. Include untracked and nested files in this integrity check.
- Use the mandatory snapshot/check/recovery procedure in change-safety after
  each potentially mutating operation and before completion. Reject and restore
  verified agent-owned violations immediately; a recovered operation still fails.
  Inspect diff/status as supporting evidence, including untracked paths.
- Run the relevant supplied questions as described in [testing.md](testing.md).
  Report actual scores, expansion counts, failures, dependency skips and interpreter.
- Do not claim assignment completion from parsing, compilation, a zero exit code,
  a hardcoded demonstration path, or documentation of intended behavior.
- State limitations when the specified environment or GUI was not verified.

## Agent-resource changes

- Maintain the root entry point, [routing](../routing.md), [repository map](../repository-map.md),
  applicable rules, workflow skills and [registry](../registry/skills.json) together.
- Run `python -B .agents/scripts/validate_agent_resources.py` from the repository root.
  This read-only check validates links, registered resources, skill metadata,
  routing fixtures and the machine-readable permission boundary.
- Run `python -B .agents/evals/test_source_guard.py` when changing the recovery
  guard. These checks use isolated temporary fixtures, never the real source tree.
- Validate new or substantially revised skills with the skill-creator
  `quick_validate.py` when available. Review realistic trigger scope as well.
- Do not import BLUEVERSE's application-specific rules or external skills merely
  to fill directories. Add overlays or third-party notices only if a real imported
  skill needs them.
- The validator checks guidance consistency; it is not an operating-system
  write lock and does not authorize source edits or prove algorithm correctness.
