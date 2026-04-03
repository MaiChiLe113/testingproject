# How to Run Each MR

## CLI Format

```
python dijkstra_algorithm.py <graph_file> <start_node> <end_node>
```

All commands below assume you are running from the repo root (the directory containing `dijkstra_algorithm.py`).

---

## MR1 — Graph Transposition

**Property:** `|SP(G, a, b)| == |SP(G^T, b, a)|`
Run SI and FI with swapped start/end. Both distances must be equal.

### MTG1

```bash
python dijkstra_algorithm.py maichi/TEST/MR1/MTG1/SI.txt A G   # expected: 11.0
python dijkstra_algorithm.py maichi/TEST/MR1/MTG1/FI.txt G A   # expected: 11.0
```

### MTG2

```bash
python dijkstra_algorithm.py maichi/TEST/MR1/MTG2/SI.txt 1 6   # expected: 5.0
python dijkstra_algorithm.py maichi/TEST/MR1/MTG2/FI.txt 6 1   # expected: 5.0
```

### MTG3

```bash
python dijkstra_algorithm.py maichi/TEST/MR1/MTG3/SI.txt P S   # expected: 8.0
python dijkstra_algorithm.py maichi/TEST/MR1/MTG3/FI.txt S P   # expected: 8.0
```

### MTG4

```bash
python dijkstra_algorithm.py maichi/TEST/MR1/MTG4/SI.txt X V   # expected: 9.0
python dijkstra_algorithm.py maichi/TEST/MR1/MTG4/FI.txt V X   # expected: 9.0
```

### MTG5

```bash
python dijkstra_algorithm.py maichi/TEST/MR1/MTG5/SI.txt S T   # expected: 3.0
python dijkstra_algorithm.py maichi/TEST/MR1/MTG5/FI.txt T S   # expected: 3.0
```

**Verdict:** SI distance == FI distance → PASS, otherwise FAIL.

---

## MR2 — Subpath Optimality

**Property:** `|SP(G, a, b)| == |SP(G, a, m)| + |SP(G, m, b)|`
Each MTG requires three executions on the same graph. The SI distance must equal FI1 distance + FI2 distance.

### MTG6

```bash
python dijkstra_algorithm.py maichi/TEST/MR2/MTG6/SI.txt  A G   # expected: 11.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG6/FI1.txt A E   # expected: 8.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG6/FI2.txt E G   # expected: 3.0
```

Additive check: `8.0 + 3.0 == 11.0`

### MTG7

```bash
python dijkstra_algorithm.py maichi/TEST/MR2/MTG7/SI.txt  1 6   # expected: 5.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG7/FI1.txt 1 3   # expected: 2.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG7/FI2.txt 3 6   # expected: 3.0
```

Additive check: `2.0 + 3.0 == 5.0`

### MTG8

```bash
python dijkstra_algorithm.py maichi/TEST/MR2/MTG8/SI.txt  M Q   # expected: 8.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG8/FI1.txt M O   # expected: 3.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG8/FI2.txt O Q   # expected: 5.0
```

Additive check: `3.0 + 5.0 == 8.0`

### MTG9

```bash
python dijkstra_algorithm.py maichi/TEST/MR2/MTG9/SI.txt  S T   # expected: 8.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG9/FI1.txt S C   # expected: 3.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG9/FI2.txt C T   # expected: 5.0
```

Additive check: `3.0 + 5.0 == 8.0`

### MTG10

```bash
python dijkstra_algorithm.py maichi/TEST/MR2/MTG10/SI.txt  X Y   # expected: 9.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG10/FI1.txt X A   # expected: 3.0
python dijkstra_algorithm.py maichi/TEST/MR2/MTG10/FI2.txt A Y   # expected: 6.0
```

Additive check: `3.0 + 6.0 == 9.0`

**Verdict:** SI distance == FI1 distance + FI2 distance → PASS, otherwise FAIL.

---

## MR3 — Input Permutation

**Property:** `|SP(G_original, a, b)| == |SP(G_permuted, a, b)|`
Run SI and FI with the same query. The graph is logically identical but lines are in a different order. Both distances must be equal.

### MTG11

```bash
python dijkstra_algorithm.py maichi/TEST/MR3/MTG11/SI.txt A G   # expected: 11.0
python dijkstra_algorithm.py maichi/TEST/MR3/MTG11/FI.txt A G   # expected: 11.0
```

### MTG12

```bash
python dijkstra_algorithm.py maichi/TEST/MR3/MTG12/SI.txt 1 6   # expected: 5.0
python dijkstra_algorithm.py maichi/TEST/MR3/MTG12/FI.txt 1 6   # expected: 5.0
```

### MTG13

```bash
python dijkstra_algorithm.py maichi/TEST/MR3/MTG13/SI.txt P T   # expected: 6.0
python dijkstra_algorithm.py maichi/TEST/MR3/MTG13/FI.txt P T   # expected: 6.0
```

### MTG14

```bash
python dijkstra_algorithm.py maichi/TEST/MR3/MTG14/SI.txt A E   # expected: 8.0
python dijkstra_algorithm.py maichi/TEST/MR3/MTG14/FI.txt A E   # expected: 8.0
```

### MTG15

```bash
python dijkstra_algorithm.py maichi/TEST/MR3/MTG15/SI.txt 1 8   # expected: 12.0
python dijkstra_algorithm.py maichi/TEST/MR3/MTG15/FI.txt 1 8   # expected: 12.0
```

**Verdict:** SI distance == FI distance → PASS, otherwise FAIL.
