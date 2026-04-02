# Mutation Testing Strategy — Dijkstra's Shortest Path Algorithm

---

## 1. Program Under Test (SUT)

**File:** `SUT/dijkstra_algorithm.py` — Python 3 implementation of Dijkstra's
single-source shortest-path algorithm on a weighted directed graph.

### 1.1 Inputs and Outputs

| Item | Description |
|------|-------------|
| **Graph file** | Plain-text; each line = `<from_node> <to_node> <weight>`. Node names are arbitrary strings; weights are non-negative floats. |
| **`shortest_path(start, end)`** | Returns `(path, distance)` where `path` is a `deque` of node names from `start` to `end` inclusive, and `distance` is the total edge-weight (`float`). |

### 1.2 Key Functions

| Function | Role |
|----------|------|
| `Graph.__init__(filename)` | Parses the file; builds `self.nodes` (set) and `self.adjacency_list` (dict of sets). |
| `Graph.shortest_path(start, end)` | Runs Dijkstra's greedy relaxation loop and reconstructs the path via a predecessor map. |

### 1.3 Algorithm Sketch

```
1.  distance[start] = 0 ;  distance[all others] = ∞
2.  previous[all] = None
3.  unvisited  = copy of all nodes
4.  while unvisited:
        current = unvisited node with smallest distance
        remove current from unvisited
        if distance[current] == ∞  → break          (disconnected)
        for each (neighbor, w) in adj[current]:
            tentative = distance[current] + w
            if tentative < distance[neighbor]:
                distance[neighbor] = tentative
                previous[neighbor] = current
        if current == end  → break                   (destination reached)
5.  back-trace previous[] from end → start to build path
6.  return (path, distance[end])
```

---

## 2. Mutation Testing Objectives

| ID | Objective |
|----|-----------|
| **O1** | Verify the test suite detects wrong **distance values** (bad arithmetic or initialisation). |
| **O2** | Verify the test suite detects wrong **path reconstruction** (wrong predecessor tracking or path-building). |
| **O3** | Verify the test suite detects **incorrect graph construction** (reversed edges, self-loops, missing nodes). |
| **O4** | Verify the test suite detects **broken loop control** (wrong termination or node-selection logic). |
| **O5** | Identify **coverage gaps** — surviving mutants reveal test-suite weaknesses. |
| **O6** | Quantify overall **fault-detection strength** (mutation score = killed / non-equivalent). |

---

## 3. Mutation Operators

| Operator | Code | Meaning |
|----------|------|---------|
| Relational Operator Replacement | **ROR** | Replaces `<`, `==`, `is not` with an alternative comparator. |
| Arithmetic Operator Replacement | **AOR** | Replaces `+` with `-`, `*`, etc. in numeric expressions. |
| Variable Replacement | **VR** | Substitutes one variable / dict-key for another of the same type. |
| Statement Deletion | **SDL** | Removes an entire statement (assignment, method call, or conditional). |
| Constant Replacement | **CR** | Replaces a literal constant with a different value. |
| Function Replacement | **FR** | Replaces a built-in call with a related alternative (`min`↔`max`, `appendleft`↔`append`). |
| Logical/Condition Replacement | **LOR** | Replaces a boolean condition (`is not None` → `is None`). |

---

## 4. Mutant Catalogue — Grouped by Objective

### O1 — Wrong Distance Values

*These mutants corrupt the numeric computation of shortest distances.*

| ID | Operator | File | Line | Original | Mutated | Effect |
|----|----------|------|------|----------|---------|--------|
| **M5** | AOR | mutant5.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] - distance` | Subtracts edge weight → negative / wrong distances |
| **M6** | AOR | mutant6.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] * distance` | Multiplies → exponentially wrong costs |
| **M7** | VR | mutant7.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[neighbor] + distance` | Uses neighbor's own stored distance — severs path accumulation |
| **M8** | VR | mutant8.py | 37 | `distance_from_start[current_node] + distance` | `distance + distance` | Ignores accumulated path cost entirely |
| **M9** | CR | mutant9.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] + distance + 1` | Adds +1 per hop — distances grow with path length, not weight |
| **M21** | CR | mutant21.py | 4 | `INFINITY = float("inf")` | `INFINITY = 0` | All nodes initialised to 0; relaxation never fires for positive weights |
| **M22** | CR | mutant22.py | 25 | `0 if node == start_node else INFINITY` | `1 if node == start_node else INFINITY` | Start biased +1 → every returned distance is off by 1 |
| **M23** | CR | mutant23.py | 25 | `0 if node == start_node else INFINITY` | `0` (always) | All nodes at distance 0; relaxation condition never satisfied |
| **M35** | VR | mutant35.py | 51 | `distance_from_start[end_node]` | `distance_from_start[start_node]` | Always returns 0 (start's own distance) regardless of destination |
| **M38** | AOR | mutant38.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] / distance` | Divides accumulated cost by edge weight → completely wrong distances |
| **M39** | CR | mutant39.py | 4 | `float("inf")` | `float("-inf")` | INFINITY sentinel is −∞; relaxation always false; distances corrupted from start |
| **M42** | VR | mutant42.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[start_node] + distance` | Base is always 0 (start dist); tentative = edge weight only, ignores path accumulation |

---

### O2 — Wrong Path Reconstruction

*These mutants produce an incorrect path list while possibly leaving distances intact.*

| ID | Operator | File | Line | Original | Mutated | Effect |
|----|----------|------|------|----------|---------|--------|
| **M16** | SDL | mutant16.py | 40 | `previous_node[neighbor] = current_node` | *(deleted)* | Predecessor map never populated; path = `[start_node]` only |
| **M17** | VR | mutant17.py | 40 | `previous_node[neighbor] = current_node` | `previous_node[neighbor] = neighbor` | Every node points to itself → **infinite loop** in reconstruction |
| **M18** | VR | mutant18.py | 40 | `previous_node[neighbor] = current_node` | `previous_node[current_node] = neighbor` | Predecessor direction reversed → wrong / crash path |
| **M24** | VR | mutant24.py | 27 | `{node: None for node in self.nodes}` | `{node: node for node in self.nodes}` | All predecessors non-None at start → **infinite loop** |
| **M31** | FR | mutant31.py | 47 | `path.appendleft(current_node)` | `path.append(current_node)` | Back-trace appended to right → path in reverse order |
| **M32** | SDL | mutant32.py | 49 | `path.appendleft(start_node)` | *(deleted)* | Start node missing from returned path |
| **M33** | VR | mutant33.py | 49 | `path.appendleft(start_node)` | `path.appendleft(end_node)` | end_node duplicated; start_node absent from path |
| **M34** | LOR | mutant34.py | 46 | `while previous_node[current_node] is not None` | `while previous_node[current_node] is None` | Loop condition inverted → reconstruction skipped; path = `[start_node]` |
| **M36** | VR | mutant36.py | 45 | `current_node = end_node` | `current_node = start_node` | Back-trace starts at start_node → reconstructs no path; returns `[start_node]` |
| **M37** | SDL | mutant37.py | 48 | `current_node = previous_node[current_node]` | *(deleted)* | Pointer never advances in loop → **infinite loop** |
| **M43** | VR | mutant43.py | 40 | `previous_node[neighbor] = current_node` | `previous_node[neighbor] = start_node` | All neighbors point to start_node → reconstruction loops or returns wrong path |

---

### O3 — Incorrect Graph Construction

*These mutants corrupt the graph data structure before the algorithm even runs.*

| ID | Operator | File | Line | Original | Mutated | Effect |
|----|----------|------|------|----------|---------|--------|
| **M27** | VR | mutant27.py | 20 | `adjacency_list[edge[0]].add((edge[1], edge[2]))` | `adjacency_list[edge[1]].add((edge[0], edge[2]))` | All edges reversed; directed graphs lose their paths |
| **M28** | VR | mutant28.py | 20 | `adjacency_list[edge[0]].add((edge[1], edge[2]))` | `adjacency_list[edge[0]].add((edge[0], edge[2]))` | Every edge becomes a self-loop; no real neighbors reachable |
| **M29** | VR | mutant29.py | 16 | `self.nodes.update([edge[0], edge[1]])` | `self.nodes.update([edge[0]])` | Destination-only nodes omitted → `KeyError` during traversal |
| **M30** | VR | mutant30.py | 12 | `(edge_from, edge_to, cost)` | `(edge_to, edge_from, cost)` | Edges reversed at parse time; same effect as M27 but earlier |
| **M44** | CR | mutant44.py | 20 | `adjacency_list[edge[0]].add((edge[1], edge[2]))` | `adjacency_list[edge[0]].add((edge[1], 1))` | All edge weights set to 1; finds fewest-hop path, not minimum-weight path |

---

### O4 — Broken Loop Control

*These mutants change how the algorithm iterates, terminates, or selects nodes.*

| ID | Operator | File | Line | Original | Mutated | Effect |
|----|----------|------|------|----------|---------|--------|
| **M10** | FR | mutant10.py | 30 | `min(unvisited_nodes, key=lambda node: distance_from_start[node])` | `max(unvisited_nodes, key=lambda node: distance_from_start[node])` | Picks farthest node each step — opposite of Dijkstra's greedy order |
| **M11** | ROR | mutant11.py | 34 | `distance_from_start[current_node] == INFINITY` | `distance_from_start[current_node] != INFINITY` | Guard inverted; breaks on first reachable node (start) — no relaxation done |
| **M12** | ROR | mutant12.py | 34 | `distance_from_start[current_node] == INFINITY` | `distance_from_start[current_node] < INFINITY` | Same early-exit effect as M11 |
| **M13** | ROR | mutant13.py | 34 | `distance_from_start[current_node] == INFINITY` | `distance_from_start[current_node] > INFINITY` | Guard is always `False` (dead code) — **potentially equivalent** on connected graphs |
| **M19** | SDL | mutant19.py | 42 | `if current_node == end_node: break` | *(deleted)* | Removes early exit — does extra work but result unchanged — **likely equivalent** |
| **M20** | VR | mutant20.py | 42 | `if current_node == end_node: break` | `if current_node == start_node: break` | Exits immediately after start; no paths beyond direct neighbours |
| **M25** | SDL | mutant25.py | 23 | `unvisited_nodes = self.nodes.copy()` | `unvisited_nodes = set()` | Empty unvisited set; loop never executes; returns `INFINITY` |
| **M26** | SDL | mutant26.py | 33 | `unvisited_nodes.remove(current_node)` | *(deleted)* | Node never removed; same node re-selected forever — **infinite loop** |
| **M41** | ROR | mutant41.py | 42 | `if current_node == end_node: break` | `if current_node != end_node: break` | Exits on first non-destination node processed — almost no relaxation performed |
| **M45** | SDL | mutant45.py | 23 | `unvisited_nodes = self.nodes.copy()` | `unvisited_nodes = self.nodes` | unvisited_nodes is live reference; `remove()` during traversal corrupts `self.nodes` |

---

### O5/O6 — Relaxation Condition (cross-cutting: affects O1 and O4)

*These mutants change the condition that decides whether to update a neighbour's distance.*

| ID | Operator | File | Line | Original | Mutated | Effect |
|----|----------|------|------|----------|---------|--------|
| **M1** | ROR | mutant1.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path <= distance_from_start[neighbor]` | Updates on equal cost too — may choose different but equally-valid path |
| **M2** | ROR | mutant2.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path > distance_from_start[neighbor]` | Updates only when new path is WORSE → stores worst distances |
| **M3** | ROR | mutant3.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path >= distance_from_start[neighbor]` | Updates on worse-or-equal → overwrites good values |
| **M4** | ROR | mutant4.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path != distance_from_start[neighbor]` | Updates on any change (better or worse) → unstable distances |
| **M14** | SDL | mutant14.py | 39 | `distance_from_start[neighbor] = new_path` | *(deleted)* | Distance table never updated; all remain at initial values |
| **M15** | VR | mutant15.py | 39 | `distance_from_start[neighbor] = new_path` | `distance_from_start[current_node] = new_path` | Updates current node's distance instead of the neighbour's |
| **M40** | ROR | mutant40.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path == distance_from_start[neighbor]` | Updates only on exact equality — almost never fires; most nodes stay at INFINITY |

---

## 5. Summary Table (all 45 mutants)

| ID | Operator | Objective | File | Line | Original Code | Mutated Code | Effect | Non-Terminate | Equivalent |
|----|----------|-----------|------|------|---------------|--------------|--------|:-------------:|:----------:|
| M1 | ROR | O5 | mutant1.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path <= distance_from_start[neighbor]` | Updates on equal cost — may choose different but equally valid path | | |
| M2 | ROR | O5 | mutant2.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path > distance_from_start[neighbor]` | Updates only when new path is worse → stores worst distances | | |
| M3 | ROR | O5 | mutant3.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path >= distance_from_start[neighbor]` | Updates on worse-or-equal → overwrites good values | | |
| M4 | ROR | O5 | mutant4.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path != distance_from_start[neighbor]` | Updates on any change (better or worse) → unstable distances | | |
| M5 | AOR | O1 | mutant5.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] - distance` | Subtracts edge weight → negative / wrong distances | | |
| M6 | AOR | O1 | mutant6.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] * distance` | Multiplies → exponentially wrong costs | | |
| M7 | VR | O1 | mutant7.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[neighbor] + distance` | Uses neighbor's own stored distance — severs path accumulation | | |
| M8 | VR | O1 | mutant8.py | 37 | `distance_from_start[current_node] + distance` | `distance + distance` | Ignores accumulated path cost entirely — tentative is 2× edge weight | | |
| M9 | CR | O1 | mutant9.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] + distance + 1` | Adds +1 per hop — distances grow with path length, not weight | | |
| M10 | FR | O4 | mutant10.py | 30 | `min(unvisited_nodes, …)` | `max(unvisited_nodes, …)` | Picks farthest node each step — opposite of Dijkstra's greedy order | | |
| M11 | ROR | O4 | mutant11.py | 34 | `distance_from_start[current_node] == INFINITY` | `distance_from_start[current_node] != INFINITY` | Guard inverted; breaks on first reachable node (start) — no relaxation done | | |
| M12 | ROR | O4 | mutant12.py | 34 | `distance_from_start[current_node] == INFINITY` | `distance_from_start[current_node] < INFINITY` | Same early-exit effect as M11 | | |
| M13 | ROR | O4 | mutant13.py | 34 | `distance_from_start[current_node] == INFINITY` | `distance_from_start[current_node] > INFINITY` | Guard always False (dead code) — never breaks early | | ✓ |
| M14 | SDL | O5 | mutant14.py | 39 | `distance_from_start[neighbor] = new_path` | *(deleted)* | Distance table never updated; all nodes remain at initial values | | |
| M15 | VR | O5 | mutant15.py | 39 | `distance_from_start[neighbor] = new_path` | `distance_from_start[current_node] = new_path` | Updates current node's distance instead of the neighbour's | | |
| M16 | SDL | O2 | mutant16.py | 40 | `previous_node[neighbor] = current_node` | *(deleted)* | Predecessor map never populated; path = `[start_node]` only | | |
| M17 | VR | O2 | mutant17.py | 40 | `previous_node[neighbor] = current_node` | `previous_node[neighbor] = neighbor` | Every node records itself as predecessor → infinite loop in reconstruction | ✓ | |
| M18 | VR | O2 | mutant18.py | 40 | `previous_node[neighbor] = current_node` | `previous_node[current_node] = neighbor` | Predecessor direction reversed → wrong or missing path | | |
| M19 | SDL | O4 | mutant19.py | 42 | `if current_node == end_node: break` | *(deleted)* | Removes early exit — does extra work but result unchanged | | ✓ |
| M20 | VR | O4 | mutant20.py | 42 | `if current_node == end_node: break` | `if current_node == start_node: break` | Exits immediately after processing start; no paths beyond direct neighbours | | |
| M21 | CR | O1 | mutant21.py | 4 | `INFINITY = float("inf")` | `INFINITY = 0` | All nodes initialised to 0; relaxation never fires for positive weights | | |
| M22 | CR | O1 | mutant22.py | 25 | `0 if node == start_node else INFINITY` | `1 if node == start_node else INFINITY` | Start node biased +1 → every returned distance is off by 1 | | |
| M23 | CR | O1 | mutant23.py | 25 | `0 if node == start_node else INFINITY` | `0` (always) | All nodes at distance 0; relaxation condition never satisfied | | |
| M24 | VR | O2 | mutant24.py | 27 | `{node: None for node in self.nodes}` | `{node: node for node in self.nodes}` | All predecessors non-None at start → infinite loop in reconstruction | ✓ | |
| M25 | SDL | O4 | mutant25.py | 23 | `unvisited_nodes = self.nodes.copy()` | `unvisited_nodes = set()` | Empty unvisited set; loop never executes; returns INFINITY | | |
| M26 | SDL | O4 | mutant26.py | 33 | `unvisited_nodes.remove(current_node)` | *(deleted)* | Node never removed; same node re-selected forever → infinite loop | ✓ | |
| M27 | VR | O3 | mutant27.py | 20 | `adjacency_list[edge[0]].add((edge[1], edge[2]))` | `adjacency_list[edge[1]].add((edge[0], edge[2]))` | All edges reversed; directed graphs lose their original paths | | |
| M28 | VR | O3 | mutant28.py | 20 | `adjacency_list[edge[0]].add((edge[1], edge[2]))` | `adjacency_list[edge[0]].add((edge[0], edge[2]))` | Every edge becomes a self-loop; no real neighbours reachable | | |
| M29 | VR | O3 | mutant29.py | 16 | `self.nodes.update([edge[0], edge[1]])` | `self.nodes.update([edge[0]])` | Destination-only nodes omitted → KeyError during traversal | | |
| M30 | VR | O3 | mutant30.py | 12 | `(edge_from, edge_to, cost)` | `(edge_to, edge_from, cost)` | Edges reversed at parse time; same effect as M27 but earlier | | |
| M31 | FR | O2 | mutant31.py | 47 | `path.appendleft(current_node)` | `path.append(current_node)` | Back-trace nodes appended to right → path returned in reverse order | | |
| M32 | SDL | O2 | mutant32.py | 49 | `path.appendleft(start_node)` | *(deleted)* | Start node never prepended; origin missing from returned path | | |
| M33 | VR | O2 | mutant33.py | 49 | `path.appendleft(start_node)` | `path.appendleft(end_node)` | end_node duplicated at front; start_node absent from path | | |
| M34 | LOR | O2 | mutant34.py | 46 | `while previous_node[current_node] is not None` | `while previous_node[current_node] is None` | Loop condition inverted → reconstruction skipped; path = `[start_node]` | | |
| M35 | VR | O1 | mutant35.py | 51 | `distance_from_start[end_node]` | `distance_from_start[start_node]` | Always returns 0 (start's own distance) regardless of destination | | |
| M36 | VR | O2 | mutant36.py | 45 | `current_node = end_node` | `current_node = start_node` | Back-trace starts at start_node → reconstructs no useful path | | |
| M37 | SDL | O2 | mutant37.py | 48 | `current_node = previous_node[current_node]` | *(deleted)* | Pointer never advances in reconstruction loop → infinite loop | ✓ | |
| M38 | AOR | O1 | mutant38.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[current_node] / distance` | Divides accumulated cost by edge weight → completely wrong distances | | |
| M39 | CR | O1 | mutant39.py | 4 | `float("inf")` | `float("-inf")` | INFINITY sentinel is −∞; distances corrupted from the start | | |
| M40 | ROR | O5 | mutant40.py | 38 | `new_path < distance_from_start[neighbor]` | `new_path == distance_from_start[neighbor]` | Updates only on exact equality — almost never fires; most nodes stay at INFINITY | | |
| M41 | ROR | O4 | mutant41.py | 42 | `if current_node == end_node: break` | `if current_node != end_node: break` | Exits on first non-destination node — almost no relaxation performed | | |
| M42 | VR | O1 | mutant42.py | 37 | `distance_from_start[current_node] + distance` | `distance_from_start[start_node] + distance` | Base always 0 (start dist); tentative = edge weight only, ignores accumulated path | | |
| M43 | VR | O2 | mutant43.py | 40 | `previous_node[neighbor] = current_node` | `previous_node[neighbor] = start_node` | All neighbours point to start_node → reconstruction loops or returns wrong path | | |
| M44 | CR | O3 | mutant44.py | 20 | `adjacency_list[edge[0]].add((edge[1], edge[2]))` | `adjacency_list[edge[0]].add((edge[1], 1))` | All edge weights replaced with 1; finds fewest-hop path, not minimum-weight path | | |
| M45 | SDL | O4 | mutant45.py | 23 | `unvisited_nodes = self.nodes.copy()` | `unvisited_nodes = self.nodes` | unvisited_nodes is a live alias; remove() during traversal corrupts self.nodes | | |

**Legend:** Non-Terminate ✓ = infinite loop (requires test timeout to kill). Equivalent ✓ = likely/potentially equivalent mutant.

**Counts:**
- Total mutants: **45**
- Likely equivalent: **2** (M13, M19)
- Non-terminating: **4** (M17, M24, M26, M37) — still non-equivalent; killed by timeout
- Non-equivalent, testable: **43**

---

## 6. How to Use This Document with the Test Suite

1. **Manual testing** — Run `python3 MUTANTS/mutantN.py` with the graph files in `TEST/`. The built-in `main()` in each mutant calls `verify_algorithm()` which asserts correct path and distance. Any `AssertionError` or `Exception` means the mutant is **killed**.

2. **Automated runner** — Use `generate_mutants.py` to regenerate all 44 programmatic mutants (M2–M45) from the current SUT: `python3 generate_mutants.py` (run from `maichi/`).

3. **Mutation score** = killed mutants ÷ non-equivalent mutants × 100 %. Target: ≥ 80 %.
