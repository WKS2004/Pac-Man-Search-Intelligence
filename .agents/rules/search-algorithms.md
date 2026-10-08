# Search algorithms and heuristic correctness

## Algorithm and heuristic constraints

- Implement graph search with expanded-state tracking. DFS must never expand
  the same state twice; avoid duplicate expansions throughout the algorithms.
- Use `util.Stack` for DFS, `util.Queue` for BFS, and `util.PriorityQueue` for
  UCS and A*. Do not substitute Python built-ins, `deque`, `heapq`, or another
  fringe implementation. Ordinary sets/dictionaries for state tracking and
  lists of actions are permitted; the fringe restriction does not prohibit them.
- Return a list of legal actions. Keep the algorithms generic over the supplied
  problem interface; do not hardcode graph states, mazes, or expected solutions.
- Check for a goal when a node is removed from the fringe. UCS priorities use
  accumulated successor costs `g`; A* priorities use `g + h` and the supplied
  heuristic argument. With `nullHeuristic`, A* must behave as UCS.
- Both assignment heuristics must be admissible and consistent. They must be
  nonnegative and zero at goal states. Explain and validate those properties;
  passing a few examples is not a mathematical proof.
- Target the PDF's full-credit expansion limits: at most 1,200 nodes for Q6 on
  `mediumCorners`, and at most 9,000 nodes for Q7 on `trickySearch`.
- Never sacrifice correctness or optimality to reduce the expansion count.

Use these PDF performance bands when discussing assignment marks, subject to
correctness and all required heuristic properties:

| Question | Expanded nodes | PDF marks |
| --- | --- | ---: |
| Q6 | More than 2,000 | 0/8 |
| Q6 | 1,601-2,000 | 4/8 |
| Q6 | 1,201-1,600 | 6/8 |
| Q6 | At most 1,200 | 8/8 |
| Q7 | More than 15,000 | 2/8 |
| Q7 | 12,001-15,000 | 4/8 |
| Q7 | 9,001-12,000 | 6/8 |
| Q7 | At most 9,000 | 8/8 |

The PDF explicitly assigns zero for Q6 if the heuristic is inadmissible or A*
returns a non-optimal path on any test, regardless of expansion count.

## Review points for the existing framework

- Keep problem states separate from action paths and accumulated cost.
- Preserve supplied successor order and priority-queue tie behavior; graph tests
  may check expansion order.
- UCS/A* must retain cheaper paths to queued states and skip stale entries without
  expanding a state unnecessarily. Do not mark a state permanently closed simply
  because it was first generated.
- `PriorityQueue.update()` compares the full item, not only its state. Account for
  that when choosing fringe entries.
- Treat food grids stored in search states as immutable. The supplied successor
  function already copies the grid before removing a dot.
- Count a corner as visited when the starting position is that corner.
- Do not copy expected paths from solution files into implementation.
