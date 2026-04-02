# MR1 Creation — Process and Reasoning

## 1. Preparing the SUT for Testing

### Problem
The original `dijkstra_algorithm.py` (and all 45 mutants) contained a `verify_algorithm()` function that hardcoded expected paths and distances and used `assert` to check them. This made it impossible to run the program as a testable unit — calling the file meant running fixed internal checks, not supplying custom inputs.

### Change
Removed `verify_algorithm()` and replaced `main()` with an `argparse` CLI interface across the SUT and all 45 mutants. The `Graph` class and `shortest_path()` method were left untouched.

```
python dijkstra_algorithm.py <filename> <start_node> <end_node>
```

### Reasoning
- Test scripts can now `import Graph` and call `shortest_path()` directly to control inputs and inspect outputs.
- The CLI allows manual verification without modifying source files.
- Separating the algorithm from its verification logic is a prerequisite for metamorphic testing — the test oracle is now external (the MR), not baked into the SUT.

---

## 2. Defining MR1 — Graph Transposition

### MR Property
```
|SP(G, a, b)| = |SP(G^T, b, a)|
```
Where `G^T` is the graph with all directed edges reversed and weights unchanged.

### Reasoning
- Dijkstra's algorithm is sensitive to edge direction — the adjacency list, neighbor traversal order, and distance updates all depend on which direction edges point.
- Transposing the graph and swapping source/destination forces the algorithm to execute a fundamentally different internal sequence (different starting node, different neighbor sets at each step) while the correct answer stays the same.
- This makes MR1 effective at catching bugs in: edge direction handling, adjacency list construction, and distance comparison logic (`<` vs `<=`).
- All constraints are preserved: non-negative weights, directed graph, connected nodes.

---

## 3. Creating the Test Graphs

### MTG-Dijkstra-Transpose-01 (MTG1)

**Source Input (`SI.txt`)** — 7-node directed graph (A–G):
```
A B 5,  A C 3,  A D 6
B C 6,  B E 4
C E 6,  C D 7
D F 2,  D E 2
E G 3,  E F 4
F G 5
```
Query: `start=A, end=G`

**Follow-up Input (`FI.txt`)** — every edge reversed:
```
B A 5,  C A 3,  D A 6, ...
```
Query: `start=G, end=A`

**Expected**: both return distance **11**.

**Reasoning — why this is a strong SI:**
- Node A branches to 3 nodes (B, C, D), creating multiple competing paths to G.
- There are at least 4 distinct routes to G (A→D→E→G, A→B→E→G, A→C→E→G, A→D→F→G).
- Reversing the graph makes G the new source, forcing the algorithm to traverse all those paths in reverse — different traversal order, different intermediate distance updates.
- The optimal path (A→D→E→G = 11) is not the greedy first choice from A, requiring the algorithm to correctly delay and update estimates.

---

### MTG-Dijkstra-Transpose-02 (MTG2)

**First version** (rejected): a near-linear 4-node graph P→Q→R→S. Only one meaningful branching point, trivial path selection — insufficient to expose logic bugs.

**Replacement — 6-node diamond graph:**

**Source Input (`SI.txt`)**:
```
1 2 4,  1 3 2
2 4 3,  2 5 7
3 4 1,  3 5 5
4 6 2
5 6 1
```
Query: `start=1, end=6`

**Follow-up Input (`FI.txt`)** — every edge reversed:
```
2 1 4,  3 1 2,  4 2 3,  5 2 7,  4 3 1,  5 3 5,  6 4 2,  6 5 1
```
Query: `start=6, end=1`

**Expected**: both return distance **5**.

Path breakdown:
| Path | Cost |
|------|------|
| 1→3→4→6 | 2+1+2 = **5** (shortest) |
| 1→3→5→6 | 2+5+1 = 8 |
| 1→2→4→6 | 4+3+2 = 9 |
| 1→2→5→6 | 4+7+1 = 12 |

**Reasoning — why this is a strong SI:**
- Two branching layers: node 1 branches to {2, 3}; both 2 and 3 connect to both {4, 5}.
- The shortest path (1→3→4→6) goes through the cheaper first hop (cost 2) then the cheaper second hop (cost 1) — not the direct or obvious route, forcing genuine priority queue comparisons.
- The transposed graph (6 as source) mirrors this structure, making the follow-up execution equally non-trivial.

---

## 4. Output Format Fix

Two minor issues were found and corrected in the SUT CLI output:
- `path` was printed as a raw `deque` object — fixed by wrapping with `list(path)`.
- `total distance` prints as `float` (e.g. `11.0`) because edge weights are parsed as `float` to support decimal costs — this is correct and intentional.

---

## 5. File Structure

```
maichi/TEST/
├── metamorphic.txt          # MR definitions and MTG table
├── MR1_creation.md          # This document
└── MR1/
    ├── MTG1/
    │   ├── SI.txt           # Source graph (7 nodes, A–G)
    │   └── FI.txt           # Transposed graph
    └── MTG2/
        ├── SI.txt           # Source graph (6 nodes, 1–6)
        └── FI.txt           # Transposed graph
```
