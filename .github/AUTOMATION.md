# GitHub collaboration and automation

This folder separates workflows, CI helpers and policies, with behavior specific
to the Pac-Man assignment.

This guide is named `AUTOMATION.md` because GitHub prioritizes a README in
`.github/` over the repository's root README. Keep the project overview and logo
in the root [README.md](../README.md).

Question ownership, supporting roles and the confirmed member order are recorded
in [the member contribution plan](../docs/member-contributions.md). Workflow
results support that plan's evidence requirements; a workflow run does not assign
authorship or establish an individual's contribution by itself.

```text
.github/
  AUTOMATION.md
  policies/
    source-policy.json
  scripts/
    check_source_boundary.py
    run_search_checks.py
    tests/
      branch-policy.test.cjs
      protected-source.test.cjs
      test_ci_helpers.py
  workflows/
    branch-policy.yml
    protected-source.yml
    repository-ci.yml
    search-tests.yml
```

## Workflows

| Workflow | Triggers | Result |
| --- | --- | --- |
| Branch Name Policy | Branch creation, branch pushes, PR updates, manual audit | Reject uppercase names and delete invalid branches in this repository |
| Protected Source Policy | PRs opened, reopened, updated or retargeted to `main` | Automatically close PRs that violate the assignment source boundary |
| Repository Checks | All branch pushes, PRs, manual runs | Validate source boundaries, Python syntax, agent resources, recovery and CI helpers; lint workflow YAML |
| Pac-Man Search Tests | All branch pushes, PRs, manual runs | Grade Q1-Q7 on Python 3.9, 3.10 and 3.11; publish score summaries and diagnostic artifacts |

CI uses read-only tokens and disables persisted checkout credentials. The
branch-policy job receives `contents: write`; the protected-source job receives
`contents: read` and `pull-requests: write`. Neither privileged policy checks out
or executes repository/PR code. Actions are pinned to verified release commits. The
actionlint archive is versioned and checked against its release SHA-256.

Automatic repository checks cover all branches and PR targets; there are no path
filters that leave those checks pending after documentation or automation-only
changes. Assignment grading also runs on branch pushes and pull requests.

## Lowercase branch policy

Every character in a branch name must already be lowercase. Examples:
`feature/q1-dfs`, `fix/corners-heuristic`, `codex/github-workflows`.
No additional prefix allowlist or `dev` integration flow is imposed.

A branch such as `Feature/q1` or `feature/Q1` is rejected and deleted, never
renamed. The failed policy check remains visible after deletion. Tag names and
branch-deletion events are ignored. A manual run audits all existing branches.

GitHub's token cannot delete branches in another owner's fork. An invalid fork
PR therefore fails the check without deleting any branch in this repository.
GitHub may refuse deletion of a default/protected branch or deny it through
repository/organization permissions; the workflow fails with that API error and
does not change protection settings. Keep the default branch lowercase (`main`).

Workflow files must be pushed before Actions can run them. Keep the branch
policy on the default branch for PR-target and manual dispatch events. GitHub
does not trigger most new workflow runs from changes made using `GITHUB_TOKEN`;
manual audits also cover branches created by such automation.
See GitHub's [event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
and [workflow triggering guide](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

## Assignment source integrity

[source-policy.json](policies/source-policy.json) records the reviewed source
baseline commit, which is preserved in Git history. Full checkout history is
required for comparisons. The boundary checker rejects protected-file changes,
additions, deletions, renames, mode/type changes and unexpected source files.
Only content edits in the existing `src/search.py` and `src/searchAgents.py`
are accepted. This CI rule does not grant agents implementation permission.

The Protected Source Policy closes violating PRs targeting `main`, including
drafts and fork PRs, as soon as its Actions run reaches the closure step. It
checks immutable Git objects against the same reviewed baseline without reading
PR-controlled policy files or running PR code. It compares the entire `src/`
tree, including nested files, modes and types, so renames, source additions,
deletions, symlink replacements and permission changes are rejected. Changes
outside `src/` remain subject to review and ordinary CI. The check assesses the
current PR source tree; changes reverted before inspection leave no violation
in that tree. No PR comments or branch deletions are made by this workflow.

Before closing, the workflow checks that the PR is still open, still targets
`main`, and still has the inspected head/base commits. A stale inspection, an
incomplete API response, or an API/permission error fails visibly rather than
approving an unverified PR. GitHub does not provide an atomic conditional close;
the final refresh minimizes, but cannot eliminate, a concurrent update race.
The trusted baseline is deliberately embedded in the default-branch workflow;
any authorized baseline revision must update it and `source-policy.json` together.

Install the workflow on the default branch and ensure GitHub Actions permits
`pull_request_target` for this repository. GitHub may block this event through
its repository/organization Actions event policy; a blocked workflow cannot
close PRs. See [GitHub's event security guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target).
A direct push to `main` has no PR to close. Existing push CI rejects source
violations, but preventing direct pushes/merges requires GitHub branch rules
and required checks, including `Reject protected source changes`. This workflow
does not undo commits already on `main` or change remote protection settings.

Changing a workflow, helper or baseline is a policy change that must be reviewed;
never advance the baseline to conceal a protected-source modification. CI checks
are not server-side branch protection or an operating-system permission lock.
Configure required checks in GitHub settings if merge enforcement is desired.
Suggested check names are `Enforce lowercase branch names`, `Repository and
source boundaries`, `GitHub workflow validation`, `Reject protected source
changes` for `main`, and the three `Q1-Q7 / Python` matrix jobs when all Python
versions should gate merges. This workflow change does not alter remote settings.

## Search grading

Pac-Man Search Tests is one workflow with three matrix jobs, one for each Python
version. It runs automatically on every branch push and pull request. Manual
dispatch remains available from GitHub's **Actions > Pac-Man Search Tests > Run
workflow**, selecting the branch to grade. Existing failed runs remain historical
records; this change does not erase them. Automatic branch, source-boundary and
repository checks remain active.

Each question runs the unchanged supplied autograder from `src/` with `-B` and
`--no-graphics`. Scores must reach the positive maximum specified by its supplied
`CONFIG`; dependency failures, missing/duplicate results, timeouts and nonzero
exit codes fail CI. A zero process exit code alone never indicates a pass.
Q8 is excluded. Local grader points differ from the PDF marks.

No additional Python packages are needed for these headless tests. The matrix
checks the PDF's Python range; it does not verify Conda setup or graphical play.
Unimplemented or incomplete questions cause the grading workflow to fail on
pushes and pull requests. Failures are not hidden with `continue-on-error`, and
grading requirements are not lowered.

The runner snapshots source before each question. Its isolated CI checkout
permits attribution of grader side effects: unauthorized changes are rejected
and restored using the existing agent source guard. Restoration never converts
the violating run to a pass. Unresolved recovery stops further questions.
Logs, JSON scores and Markdown summaries go to runner temporary storage and
artifacts, never `src/`. Reports are created exclusively in a fresh results
directory; existing report paths are rejected instead of overwritten. The source
check runs after each question's diagnostic write. Step summaries reject
hard-link aliases and protected destinations. Artifacts expire after seven days.

## Local validation

From the repository root:

```text
python -B .github/scripts/check_source_boundary.py
python -B .agents/scripts/validate_agent_resources.py
python -B .agents/evals/test_source_guard.py
python -B -m unittest discover -s .github/scripts/tests -p "test_*.py"
node --test .github/scripts/tests/*.test.cjs
actionlint -shellcheck= -pyflakes=
python -B .github/scripts/run_search_checks.py --results-dir ABSOLUTE_TEMP_DIRECTORY
```

The helper regression tests use isolated temporary fixtures. Workflow policy tests
mock GitHub APIs; they do not delete remote branches or close real PRs. The grading runner assumes
an exclusive source workspace: do not run it while another person/process is
editing the source. Agents sharing a live workspace must follow the ownership
checks in the universal change-safety rule instead of assuming every diff is theirs.
