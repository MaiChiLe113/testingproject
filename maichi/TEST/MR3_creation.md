# MR3 Creation — Process and Reasoning

## 1. Defining MR3 — Input Permutation

### MR Property
```
|SP(G_original, a, b)| = |SP(G_permuted, a, b)|
```
Where `G_permuted` is the same logical graph as `G_original` but with its edge lines written in a different order inside the input file.

### Reasoning
- The SUT reads the graph from a text file line by line, inserting each edge into an adjacency list (typically a Python `dict` or `defaultdict`). The correctness of that adjacency list must not depend on the sequence in which edges appear in the file.
- If the parser or adjacency-list builder stores data incorrectly — for example, overwriting earlier edges of the same source node rather than appending them, or failing to group edges that belong to the same node when they appear non-consecutively — then permuting the file will produce a different (wrong) graph, and the shortest-path distance will change.
- MR3 is therefore specifically designed to stress-test the **file parser and adjacency-list construction**, isolating those components from the Dijkstra traversal logic itself (which MR1 and MR2 target more directly).
- The query (start and end nodes) and all edge weights are kept identical across SI and FI. Only the line order changes.

### Constraint Alignment
- **Unique node labels:** Permutation does not rename nodes; the same identifiers appear in both files.
- **Non-negative weights:** Shuffling lines does not alter weight values.
- **Deterministic output:** Because the graph is logically identical, the algorithm must produce the same distance on every run, regardless of file order.
- **Connected nodes:** The same edge set guarantees the same connectivity in both SI and FI.

---

## 2. Permutation Strategy

Three distinct shuffling strategies are used across the five MTGs to cover different parser failure modes:

| Strategy | MTGs | What it tests |
|----------|------|---------------|
| **Random shuffle** | MTG11 | General order-independence; edges of same source are fully scattered |
| **Full reversal** | MTG12 | Parser reads lines bottom-to-top vs. top-to-bottom — catches array-based builders |
| **Source grouping swap** | MTG13, MTG14 | Edges of the same source node appear non-consecutively in SI but are grouped in FI (or vice versa) — targets `dict` builders that might overwrite keys |
| **Scattered multi-source** | MTG15 | A large graph with completely shuffled lines, ensuring no accidental ordering assumptions hold |

---

## 3. Creating the Test Graphs

### MTG-Dijkstra-Permute-11 (MTG11)

**Source Input (`SI.txt`)** — 7-node directed graph (A–G), same graph as MR1 MTG1, edges in natural source-alphabetical order:
```
A B 5,  A C 3,  A D 6
B C 6,  B E 4
C E 6,  C D 7
D F 2,  D E 2
E G 3,  E F 4
F G 5
```
Query: `start=A, end=G`, SO = **11**

**Follow-up Input (`FI.txt`)** — same 12 edges, randomly shuffled (F-edges lead, then D/E interior edges, then others):
```
F G 5
D E 2
E G 3
A C 3
B E 4
C D 7
D F 2
A B 5
E F 4
C E 6
A D 6
B C 6
```
Query: `start=A, end=G`, expected = **11**

**Reasoning — why this is a strong test:**
- With 12 edges and 7 nodes, there are many possible orderings. The shuffle specifically moves `F G 5` to the first line and scatters all A-source edges (originally lines 1–3) to positions 4, 8, 11. A buggy parser that reads only the first occurrence of a source key would build a graph where A has only one outgoing edge (A C 3) instead of three, causing the algorithm to miss the optimal A→D→E→G path.
- The known optimal path (distance 11) requires visiting all three of A's neighbours, so any adjacency-list truncation is immediately detectable.

---

### MTG-Dijkstra-Permute-12 (MTG12)

**Source Input (`SI.txt`)** — 6-node diamond graph (1–6), standard order:
```
1 2 4,  1 3 2
2 4 3,  2 5 7
3 4 1,  3 5 5
4 6 2
5 6 1
```
Query: `start=1, end=6`, SO = **5**

**Follow-up Input (`FI.txt`)** — all 8 lines in exact reverse order:
```
5 6 1
4 6 2
3 5 5
3 4 1
2 5 7
2 4 3
1 3 2
1 2 4
```
Query: `start=1, end=6`, expected = **5**

**Reasoning — why this is a strong test:**
- Full reversal is the most common ordering assumed by naïve array-based parsers that process lines sequentially and discard earlier records. With full reversal, node 1's edges appear last (at the bottom) — if the parser depends on seeing the source node first to initialise its entry, or if it uses a list and searches linearly, it may fail to include those edges.
- The diamond structure has 4 distinct paths (costs 5, 8, 9, 12). The parser must correctly reconstruct all 4 route options from the reversed file, not just the path whose edges happen to appear first.
- Node 5's edge (5→6=1) becomes line 1 in FI, meaning the "destination edge" of the longest path appears before the source edges of node 1. A correct parser is unaffected; a broken one may fail to connect node 1 to anything.

---

### MTG-Dijkstra-Permute-13 (MTG13)

**Source Input (`SI.txt`)** — 6-node graph (P–T) with non-consecutive P-edges:
```
P Q 4   ← P-edge at line 1
R S 2
P R 1   ← P-edge at line 3
S T 3
P S 10  ← P-edge at line 5
Q T 5
```
Query: `start=P, end=T`, SO = **6** (path: P→R→S→T)

Path analysis:
| Path | Cost |
|------|------|
| P→R→S→T | 1+2+3 = **6** (shortest) |
| P→Q→T | 4+5 = 9 |
| P→S→T | 10+3 = 13 |

**Follow-up Input (`FI.txt`)** — P's three edges grouped consecutively at the top:
```
P Q 4
P R 1
P S 10
R S 2
S T 3
Q T 5
```
Query: `start=P, end=T`, expected = **6**

**Reasoning — why this is a strong test:**
- In SI, node P's three outgoing edges appear at lines 1, 3, and 5 — interleaved with edges of other nodes. A parser that processes edges into a dict correctly (e.g., `graph[source].append(...)`) handles this fine; one that uses assignment (`graph[source] = [dest, weight]`) will overwrite, keeping only the last edge (P S 10) and discarding P→Q and P→R.
- In FI, P's edges are grouped together, which would "pass" a naïve overwriting parser by accident (it would keep the last P-edge, P S 10 — still wrong, but the failure mode is more obvious when SI is checked too). Comparing SI vs. FI results therefore reveals whether the failure is systematic.
- The optimal path P→R→S→T (distance 6) depends on P→R being correctly stored. If P→R is discarded, the best available path becomes P→Q→T = 9, which is a clear and detectable violation of the MR.

---

### MTG-Dijkstra-Permute-14 (MTG14)

**Source Input (`SI.txt`)** — 5-node graph (A–E) with interspersed A-edges:
```
A B 2   ← A-edge at line 1
C D 4
A C 3   ← A-edge at line 3
D E 1
B E 7
A D 8   ← A-edge at line 6
```
Query: `start=A, end=E`, SO = **8** (path: A→C→D→E)

Path analysis:
| Path | Cost |
|------|------|
| A→C→D→E | 3+4+1 = **8** (shortest) |
| A→B→E | 2+7 = 9 |
| A→D→E | 8+1 = 9 |

**Follow-up Input (`FI.txt`)** — interior edges (C→D, D→E, B→E) moved to the top; all A-edges grouped at the bottom:
```
C D 4
D E 1
B E 7
A B 2
A C 3
A D 8
```
Query: `start=A, end=E`, expected = **8**

**Reasoning — why this is a strong test:**
- In FI, C→D and D→E appear before any A-edge. A parser that requires source nodes to appear before their descendants (e.g., a streaming builder that skips forward references) would fail to link these edges into A's reachable subgraph.
- In SI, A-edges are split across three non-adjacent lines. Correctly assembling all of A's edges from SI requires the parser to accumulate, not overwrite, entries for the same key.
- The distinction between the optimal path (A→C→D→E = 8) and the two suboptimal paths (both cost 9) is small (1 unit). Any loss of an A-edge causes the algorithm to return 9 instead of 8 — detectable but not dramatically different, making this a precise test of correct construction.
- MTG14 complements MTG13 by using a different graph topology (linear convergence instead of a hub) and a different grouping pattern (non-adjacent in SI, grouped in FI — the opposite direction from MTG3).

---

### MTG-Dijkstra-Permute-15 (MTG15)

**Source Input (`SI.txt`)** — 8-node graph (1–8) in natural edge order:
```
1 2 3
1 3 7
2 4 2
3 4 1
4 5 4
2 5 10
3 6 5
5 7 2
6 7 3
7 8 1
```
Query: `start=1, end=8`, SO = **12** (path: 1→2→4→5→7→8)

Path analysis (all routes from 1 to 8):
| Path | Cost |
|------|------|
| 1→2→4→5→7→8 | 3+2+4+2+1 = **12** (shortest) |
| 1→3→4→5→7→8 | 7+1+4+2+1 = 15 |
| 1→2→5→7→8 | 3+10+2+1 = 16 |
| 1→3→6→7→8 | 7+5+3+1 = 16 |

**Follow-up Input (`FI.txt`)** — all 10 lines fully shuffled (terminal edges first, source edges last):
```
7 8 1
3 6 5
4 5 4
1 3 7
6 7 3
2 5 10
1 2 3
5 7 2
3 4 1
2 4 2
```
Query: `start=1, end=8`, expected = **12**

**Reasoning — why this is a strong test:**
- With 10 edges and 8 nodes, this is the largest graph in the MR3 suite. The full shuffle places terminal edges (7→8=1, which is the last hop of the optimal path) at the very beginning of FI, while node 1's two outgoing edges appear at lines 4 and 7 — far apart and embedded among other nodes' edges.
- The optimal path 1→2→4→5→7→8 spans 5 hops across 4 different source nodes (1, 2, 4, 5, 7). Every one of those source nodes has its edge appearing in a different position in FI compared to SI. A correct parser assembles all edges identically regardless of file order; a broken one will produce a subtly incomplete adjacency list.
- The large graph also tests for performance-degrading bugs: if the parser iterates the full edge list for each node lookup (O(E) per node) rather than using a hash map, the ordering change would expose that inefficiency — though the primary check remains on correctness of the output distance.
- MTG15 acts as a stress test that subsumes the concerns of MTG11–14 in a single, more complex scenario.

---

## 4. File Structure

```
maichi/TEST/
├── MR3_creation.md          # This document
└── MR3/
    ├── MTG11/
    │   ├── SI.txt           # 7-node A–G graph; edges in natural order; query A→G (distance 11)
    │   └── FI.txt           # Same 12 edges, randomly shuffled
    ├── MTG12/
    │   ├── SI.txt           # Diamond 1–6 graph; standard order; query 1→6 (distance 5)
    │   └── FI.txt           # Same 8 edges, fully reversed
    ├── MTG13/
    │   ├── SI.txt           # P–T graph; P-edges at lines 1,3,5 (non-consecutive); query P→T (distance 6)
    │   └── FI.txt           # Same 6 edges; P-edges grouped at lines 1,2,3
    ├── MTG14/
    │   ├── SI.txt           # A–E graph; A-edges at lines 1,3,6 (non-consecutive); query A→E (distance 8)
    │   └── FI.txt           # Same 6 edges; interior edges first, A-edges grouped at lines 4,5,6
    └── MTG15/
        ├── SI.txt           # 8-node 1–8 graph; edges in natural order; query 1→8 (distance 12)
        └── FI.txt           # Same 10 edges, fully shuffled (terminal edges first)
```
