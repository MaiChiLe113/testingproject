# MR2 Creation — Process and Reasoning

## 1. Defining MR2 — Subpath Optimality

### MR Property
```
|SP(G, a, b)| = |SP(G, a, m)| + |SP(G, m, b)|
```
Where `m` is any intermediate node on the optimal path from `a` to `b`, and `SP(G, x, y)` denotes the shortest path distance between nodes `x` and `y` on graph `G`.

### Reasoning
- Dijkstra's algorithm is built on the principle of optimal substructure: if the shortest path from A to G passes through node E, then the A→E segment of that path must itself be the shortest path from A to E. Any violation of this property reveals that the algorithm either failed to fully relax some edge, settled on a suboptimal path early, or made an incorrect distance comparison.
- Unlike MR1 (which changes the graph itself), MR2 keeps the graph fixed and changes the query. This isolates bugs in the **relaxation loop and priority queue logic** rather than in parsing or adjacency-list construction.
- The graph file in FI1 and FI2 is identical to SI. Only the CLI arguments (start and end nodes) change, so the same graph object is re-used with different source/destination pairs. This design makes it straightforward to run all three executions and compare distances programmatically.

### Constraint Alignment
- **Connected nodes guaranteed:** The intermediate node `m` is extracted directly from the source output path. Because `m` already appears in a valid path from `a` to `b`, both `a→m` and `m→b` are reachable by construction.
- **Non-negative weights preserved:** The graph is unchanged across all three executions; weights remain the same positive values.
- **Additive relation:** The verdict is `|SP(G, a, b)| == |SP(G, a, m)| + |SP(G, m, b)|`. Any mismatch exposes an optimality failure.

---

## 2. Execution Model

Each MTG requires three CLI executions on the same graph file:

```
python dijkstra_algorithm.py MR2/MTGn/SI.txt  <start>  <end>         # Source
python dijkstra_algorithm.py MR2/MTGn/FI1.txt <start>  <mid>         # Follow-up 1
python dijkstra_algorithm.py MR2/MTGn/FI2.txt <mid>    <end>         # Follow-up 2
```

`FI1.txt` and `FI2.txt` contain the same graph as `SI.txt`. They exist as separate files so that each execution is self-contained and runnable with an identical command pattern.

---

## 3. Creating the Test Graphs

### MTG-Dijkstra-Subpath-01 (MTG1)

**Source Input (`SI.txt`)** — 7-node directed graph (A–G), reused from MR1 MTG1:
```
A B 5,  A C 3,  A D 6
B C 6,  B E 4
C E 6,  C D 7
D F 2,  D E 2
E G 3,  E F 4
F G 5
```
Query: `start=A, end=G` → SO path: `['A', 'D', 'E', 'G']`, distance **11**

**Intermediate node:** E (3rd node in path)

**Follow-up queries:**
| Execution | Query | All paths | Distance |
|-----------|-------|-----------|----------|
| FI1 | A → E | A→D→E = 6+2 = **8**; A→B→E = 9; A→C→E = 9 | **8** |
| FI2 | E → G | E→G = **3**; E→F→G = 9 | **3** |

**Additive check:** 8 + 3 = **11** ✓

**Reasoning — why this is a strong test:**
- Node A has three outgoing edges (B, C, D), giving the algorithm real competition at the first step.
- The shortest path A→D→E→G does not use the cheapest first hop (A→C=3 is cheaper than A→D=6), so a greedy bug that short-circuits after finding A→C would fail.
- When testing A→E (FI1), the same greedy trap exists: A→C→E = 9 but A→D→E = 8, forcing correct relaxation.
- E→G (FI2) is a single direct edge, making the subpath check trivially verifiable — any wrong answer here would indicate a severe algorithm failure.

---

### MTG-Dijkstra-Subpath-02 (MTG2)

**Source Input (`SI.txt`)** — 6-node diamond graph, reused from MR1 MTG2:
```
1 2 4,  1 3 2
2 4 3,  2 5 7
3 4 1,  3 5 5
4 6 2
5 6 1
```
Query: `start=1, end=6` → SO path: `['1', '3', '4', '6']`, distance **5**

**Intermediate node:** 3 (2nd node in path)

**Follow-up queries:**
| Execution | Query | All paths | Distance |
|-----------|-------|-----------|----------|
| FI1 | 1 → 3 | 1→3 = **2** (direct) | **2** |
| FI2 | 3 → 6 | 3→4→6 = 1+2 = **3**; 3→5→6 = 5+1 = 6 | **3** |

**Additive check:** 2 + 3 = **5** ✓

**Reasoning — why this is a strong test:**
- The intermediate (node 3) is the very first hop in the optimal path. FI1 therefore tests whether the algorithm correctly initialises the source distance to 0 and expands to immediate neighbours.
- FI2 (3→6) is a mini two-branch problem: 3→4→6 vs 3→5→6. This sub-problem by itself exercises branching and relaxation, making it a meaningful test even in isolation.
- Together they confirm that the globally optimal path is assembled from locally optimal subpaths — the core invariant of Dijkstra's correctness.

---

### MTG-Dijkstra-Subpath-03 (MTG3)

**Source Input (`SI.txt`)** — 6-node linear-branching graph (M–Q):
```
M N 2,  M O 8
N P 3,  N O 1
O P 1
P Q 4
```
Query: `start=M, end=Q` → SO path: `['M', 'N', 'O', 'P', 'Q']`, distance **8**

Path analysis:
| Path | Cost |
|------|------|
| M→N→O→P→Q | 2+1+1+4 = **8** (shortest) |
| M→N→P→Q | 2+3+4 = 9 |
| M→O→P→Q | 8+1+4 = 13 |

**Intermediate node:** O (3rd node in path)

**Follow-up queries:**
| Execution | Query | All paths | Distance |
|-----------|-------|-----------|----------|
| FI1 | M → O | M→N→O = 2+1 = **3**; M→O = 8 | **3** |
| FI2 | O → Q | O→P→Q = 1+4 = **5** | **5** |

**Additive check:** 3 + 5 = **8** ✓

**Reasoning — why this is a strong test:**
- The direct edge M→O (cost 8) is a decoy. The algorithm must discover the cheaper two-hop route M→N→O (cost 3) via relaxation. If it settles on M→O = 8 without further exploration, FI1 returns 8 instead of 3, causing the relation to fail.
- The 4-hop path M→N→O→P→Q is the optimal source path, so the intermediate O sits in the middle of the path — a position that exercises relaxation across several iterations of the priority queue.
- This graph also tests that the algorithm does not prematurely terminate when it first reaches Q via the suboptimal M→N→P→Q path.

---

### MTG-Dijkstra-Subpath-04 (MTG4)

**Source Input (`SI.txt`)** — 7-node convergence graph (S–T):
```
S A 1,  S B 5
A C 2,  A D 10
B C 1
C D 3
D T 2
```
Query: `start=S, end=T` → SO path: `['S', 'A', 'C', 'D', 'T']`, distance **8**

Path analysis:
| Path | Cost |
|------|------|
| S→A→C→D→T | 1+2+3+2 = **8** (shortest) |
| S→B→C→D→T | 5+1+3+2 = 11 |
| S→A→D→T | 1+10+2 = 13 |

**Intermediate node:** C (3rd node in path)

**Follow-up queries:**
| Execution | Query | All paths | Distance |
|-----------|-------|-----------|----------|
| FI1 | S → C | S→A→C = 1+2 = **3**; S→B→C = 5+1 = 6 | **3** |
| FI2 | C → T | C→D→T = 3+2 = **5** | **5** |

**Additive check:** 3 + 5 = **8** ✓

**Reasoning — why this is a strong test:**
- Node C is a convergence point: both branches from S (via A and via B) funnel into C. This creates a scenario where the algorithm must update C's distance twice — first when A is settled (distance 3) and again if B is settled (distance 6 > 3, so no update). Bugs in the `<` vs `<=` comparison or in skipping already-settled nodes could corrupt C's final distance.
- The intermediate is chosen at the convergence point C, meaning FI1 (S→C) directly tests this multi-path update scenario in isolation.
- FI2 (C→T) is a single linear chain C→D→T, acting as a sanity baseline — if FI2 fails, the bug is in the simplest possible path traversal.

---

### MTG-Dijkstra-Subpath-05 (MTG5)

**Source Input (`SI.txt`)** — 6-node fan-out graph (X–Y):
```
X A 3,  X B 10
A B 2,  A C 5
B Y 4
C Y 2
```
Query: `start=X, end=Y` → SO path: `['X', 'A', 'B', 'Y']`, distance **9**

Path analysis:
| Path | Cost |
|------|------|
| X→A→B→Y | 3+2+4 = **9** (shortest) |
| X→A→C→Y | 3+5+2 = 10 |
| X→B→Y | 10+4 = 14 |

**Intermediate node:** A (2nd node in path)

**Follow-up queries:**
| Execution | Query | All paths | Distance |
|-----------|-------|-----------|----------|
| FI1 | X → A | X→A = **3** (direct); X→B→? (B has no path back to A) | **3** |
| FI2 | A → Y | A→B→Y = 2+4 = **6**; A→C→Y = 5+2 = 7 | **6** |

**Additive check:** 3 + 6 = **9** ✓

**Reasoning — why this is a strong test:**
- The intermediate node A is the immediate successor of the source X. FI1 is therefore a trivial single-edge query — if the algorithm gets this wrong, it indicates a fundamental initialisation bug.
- FI2 (A→Y) is itself a two-branch sub-problem (A→B→Y vs A→C→Y), requiring Dijkstra to correctly prefer the 6-cost route over the 7-cost route. This makes the follow-up a meaningful mini-test.
- The large direct edge X→B = 10 serves as a decoy in the source execution; the algorithm must correctly prefer X→A = 3 despite B being reachable in one hop.
- This MTG complements MTG4 by placing the intermediate at the first hop rather than the middle, covering a different structural position within the path.

---

## 4. File Structure

```
maichi/TEST/
├── MR2_creation.md          # This document
└── MR2/
    ├── MTG1/
    │   ├── SI.txt           # 7-node A–G graph; query A→G (distance 11)
    │   ├── FI1.txt          # Same graph; query A→E (distance 8)
    │   └── FI2.txt          # Same graph; query E→G (distance 3)
    ├── MTG2/
    │   ├── SI.txt           # Diamond 1–6 graph; query 1→6 (distance 5)
    │   ├── FI1.txt          # Same graph; query 1→3 (distance 2)
    │   └── FI2.txt          # Same graph; query 3→6 (distance 3)
    ├── MTG3/
    │   ├── SI.txt           # M–Q graph; query M→Q (distance 8)
    │   ├── FI1.txt          # Same graph; query M→O (distance 3)
    │   └── FI2.txt          # Same graph; query O→Q (distance 5)
    ├── MTG4/
    │   ├── SI.txt           # S–T convergence graph; query S→T (distance 8)
    │   ├── FI1.txt          # Same graph; query S→C (distance 3)
    │   └── FI2.txt          # Same graph; query C→T (distance 5)
    └── MTG5/
        ├── SI.txt           # X–Y fan-out graph; query X→Y (distance 9)
        ├── FI1.txt          # Same graph; query X→A (distance 3)
        └── FI2.txt          # Same graph; query A→Y (distance 6)
```
