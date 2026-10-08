# Scope, authorization and protected files

## Authority and current permission

- Follow the user's instructions and the assignment-specific requirements in the
  Project Guidelines PDF. Do not silently resolve conflicting requirements.
- The user initially authorized read-only analysis. The subsequent request to
  implement these rules authorizes repository instruction files only. It does
  **not** authorize implementing algorithms or modifying assignment source files.
- Until the user explicitly authorizes source implementation, treat every file
  under `src/` and the existing `README.md` as read-only.
- After implementation is authorized, apply the source edit allowlist below.
  A request to implement or fix the assignment is not permission to edit the
  supplied framework, tests, layouts, or grading configuration.
- Change repository instructions, reports, evidence, environment configuration,
  or submission artifacts only within the user's authorized task scope. Never
  infer permission to change protected assignment files from a failing test.

## Strict source edit allowlist

When source implementation is explicitly authorized, agents may edit only these
two existing assignment source files:

1. `src/search.py`
2. `src/searchAgents.py`

Within those files, implement only the requested assignment portions. Preserve
the supplied interfaces, function signatures, aliases, class names, licensing
notices, and attribution. Do not rewrite unrelated supplied code.

Every other file anywhere under `src/` is strictly read-only. This applies to
supplied files, user-added files, untracked files and all nested directories;
the examples below are not an exhaustive boundary:

- `src/util.py`: use its data structures; do not modify or replace them.
- `src/pacman.py`, `src/game.py`, `src/layout.py`.
- `src/autograder.py`, `src/grading.py`, `src/projectParams.py`.
- `src/searchTestClasses.py`, `src/testClasses.py`, `src/testParser.py`.
- `src/graphicsDisplay.py`, `src/graphicsUtils.py`, `src/textDisplay.py`.
- `src/ghostAgents.py`, `src/pacmanAgents.py`, `src/keyboardAgents.py`.
- `src/eightpuzzle.py`, `src/VERSION`.
- All files under `src/layouts/` and `src/test_cases/`, including `CONFIG`,
  `.test`, and `.solution` files.
- Any other supplied file not explicitly on the two-file allowlist.

## Prohibited operations throughout src

- Do not create any new file under `src/`, including tests, helpers, instruction
  files, configuration, logs, reports, archives, bytecode or generated outputs.
- Do not delete, rename or move files under `src/`, including the two editable
  files. Permission to edit their contents does not authorize structural changes.
- Do not overwrite, format, normalize line endings, restore from Git, copy over,
  or otherwise change any file outside the two-file allowlist, whether directly
  or through a script, formatter, test runner or other tool. The only recovery
  exception is undoing a verified agent-owned violation as described below.
- If an allowed file is missing or resolves outside this repository, report the
  condition. Do not recreate it, replace a link, or use another path as a workaround.
- Put any separately authorized artifacts outside `src/`. Disable tool outputs
  that would write there. A tool's automatic side effects are still file changes.
- Broad requests to implement, debug, test, refactor, finalize or package do not
  broaden this restriction. Only a direct user instruction explicitly revising
  the file boundary can change it; skills and agent decisions cannot.

Do not modify test expectations, grading weights, dependencies, thresholds,
timeouts, or layouts to make a solution pass. Report defects in protected files;
do not repair them as part of ordinary assignment implementation.

## Mandatory rejection and recovery

- Reject unauthorized changes to any file under `src/` automatically. In a
  read-only task this includes both normally editable files. Authorized content
  edits to the two existing allowed files remain permitted; structural changes
  and tool-generated files remain violations in every task.
- Before any agent operation, capture the current complete source tree with
  [source_guard.py](../scripts/source_guard.py) using `snapshot`. Keep its printed
  snapshot path for the task; do not replace a baseline after a suspected violation.
  Snapshots live in temporary storage, never under `src/` or BLUEVERSE. If the
  tool sandbox discards its temporary directory between calls, use `snapshot
  --directory PERSISTENT_TEMP_DIRECTORY`, or retain the helper's `capture` result
  in memory and pass it to `check`. A missing snapshot is a failed gate.
- Run `check` after every agent operation that could affect source and before
  reporting completion, including after errors, interruptions and failed tests.
  Use `--authorized-source-edit` only when the user authorized implementation;
  the flag itself does not establish authorization.
- When a violation is attributable to the agent or its tools, the agent must
  immediately provide its recorded post-operation fingerprint using `--owned`
  and let the check restore it automatically. No additional user permission is
  needed to undo that agent-owned violation. Never mark an unexplained difference
  as agent-owned merely to make the check pass.
- Restoration means the verified pre-task bytes, file mode and modification time,
  including pre-existing local edits and untracked files. Undo agent-created
  files/directories and restore agent-deleted files/directories; a rename requires
  recovery of both affected paths. The rejected operation stays a failure even
  after successful recovery. Recheck until the protected tree is clean.
- Fingerprints include content and metadata. Record the agent's own resulting
  fingerprint before unrelated work can intervene. The guard refuses to restore
  a path whose current fingerprint differs from that record, or whose ownership
  is unknown. Preserve possible concurrent user edits, stop affected work, and
  report the unresolved conflict. Do not guess or overwrite it.
- Never use blanket `git reset`, `git restore`, checkout, or a starter copy for
  recovery. Git HEAD is not necessarily the user's pre-task state. If an earlier
  agent violation is discovered, recover it only from a trustworthy original and
  verified attribution; report missing evidence instead of inventing originals.
- The guard rejects symbolic links/junctions and unsafe paths. Do not bypass it
  if capture, checking or recovery fails. Keep the snapshot until verification
  and any recovery finish. This procedure is mandatory for all agents and routes.

From the repository root (use the available Python interpreter):

```text
python -B .agents/scripts/source_guard.py snapshot
python -B .agents/scripts/source_guard.py check SNAPSHOT_PATH
python -B .agents/scripts/source_guard.py check SNAPSHOT_PATH --owned src/util.py=RECORDED_FINGERPRINT
```

`check` reports each violating path's fingerprint. That output is evidence of
current state, not proof of ownership. Supply `--owned` only for changes traced
to the agent's operation; repeat it for each confirmed path. The guard checks the
fingerprint again before restoring and returns failure when any violation was
detected, even if restored. It is an explicit check/recovery tool, not a background
watcher or an operating-system write lock. Instructions require agents to invoke it.

## Reference projects and instruction maintenance

- BLUEVERSE's `.agents` and root instructions are read-only structural references,
  not this project's requirements. Do not execute its workflows or alter its files.
- Preserve user changes. Inspect status and relevant paths before editing.
- Ordinary assignment implementation must not rewrite `.agents` policy.
  Agent-resource edits require a user request or applicable existing authorization.
- Supporting scripts, registry and evaluation fixtures under `.agents/` are agent
  resources, not additional assignment source or submission files.
- If an explicit later user instruction changes scope, apply it without treating
  this historical permission record as permanent denial. Keep the PDF restrictions
  visible and clarify genuine assignment conflicts when a decision depends on them.
