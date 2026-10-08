# Environment and assignment verification

## Environment and verification

- The PDF specifies Python 3.9-3.11 and gives a Conda environment named `cs188`
  using Python 3.11, with `numpy` and `matplotlib` installed. Do not create an
  environment or install dependencies under analysis-only authorization.
- Distinguish verification with another available interpreter from verification
  in the specified assignment environment.
- For authorized read-only verification, disable bytecode writes with `python
  -B`. Do not create `__pycache__`, logs, test outputs, or other project artifacts.
- Never use `--generate-solutions`, `--edx-output`, or `--gradescope-output`
  during read-only verification. Do not record games or enable frame export.
- From `src/`, the per-question headless verification commands are:

  ```text
  python -B autograder.py -q q1 --no-graphics
  python -B autograder.py -q q2 --no-graphics
  python -B autograder.py -q q3 --no-graphics
  python -B autograder.py -q q4 --no-graphics
  python -B autograder.py -q q5 --no-graphics
  python -B autograder.py -q q6 --no-graphics
  python -B autograder.py -q q7 --no-graphics
  ```

- Per-question commands may also run dependencies. A full run includes Q8;
  distinguish its results from the assessed Q1-Q7 results.
- Verify legal paths, optimality where required, heuristic properties, expansion
  counts, and runtime. Report skipped tests and unverified GUI behavior clearly.
- Snapshot source before testing and check it after every command, including
  failed commands. Automatically reject and restore verified agent-owned side
  effects under the universal change-safety recovery procedure.

## Focused verification

- The source-tree restriction applies to every run, including testing authorized
  implementation: use `-B` and keep caches, logs, recordings, screenshots, test
  outputs and all other generated files outside `src/` when separately authorized.
- Q5 depends on BFS; Q6 and Q7 depend on A*. Dependency skips are not passing tests.
- A passing process exit code is not enough: the grader can exit successfully
  while reporting failed questions. Read the actual per-question scores/messages.
- Use supplied tests unchanged. Additional probes may run in memory under the
  authorized scope; do not add files to `src/test_cases/`.
- Heuristic verification includes nontriviality where supplied tests require it,
  empty-food/goal behavior, admissibility, consistency, optimal path cost and
  performance. Distinguish mathematical reasoning from observed test evidence.
- GUI play is a separate environment check. Importing graphics or winning a
  headless game does not prove keyboard play works.
