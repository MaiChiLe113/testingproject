"""
MR2 Mutation Testing Runner
Runs all 45 mutants against MR2 (Subpath Optimality) test groups MTG6-MTG10.
MR2 property: SP(G, a, c) = SP(G, a, b) + SP(G, b, c)  where b lies on the optimal path.
Results are printed to terminal and saved to MR2_mutant_evaluation.csv.
Run from project root: python maichi/run_mr2_tests.py
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
MUTANTS_DIR = BASE / "MUTANTS"
MR2_DIR = BASE / "TEST" / "MR2"
MUTANT_CSV = BASE / "Mutant.csv"
OUTPUT_CSV = BASE / "MR2_mutant_evaluation.csv"
TIMEOUT = 10  # seconds

# (mtg_name, si_start, si_end, fi1_start, fi1_end, fi2_start, fi2_end)
# All three inputs (SI, FI1, FI2) share the same graph file per MTG.
MTG_CONFIGS = [
    ("MTG6",  "A", "G", "A", "E", "E", "G"),
    ("MTG7",  "1", "6", "1", "3", "3", "6"),
    ("MTG8",  "M", "Q", "M", "O", "O", "Q"),
    ("MTG9",  "S", "T", "S", "C", "C", "T"),
    ("MTG10", "X", "Y", "X", "A", "A", "Y"),
]

FIELDNAMES = [
    "Mutant ID",
    "MTG ID",
    "Status",
    "Notes",
    "Actual Output SI",
    "Actual Output FI1",
    "Actual Output FI2",
    "Actual Output Relation",
    "MR Verdict",
]


def load_mutant_metadata():
    meta = {}
    with open(MUTANT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = row["ID"].strip()
            meta[mid] = {
                "equivalent": row["Equivalent"].strip().lower() == "yes",
            }
    return meta


def run_cmd(mutant_file, graph_file, start, end):
    """Run mutant CLI, return (stdout, timed_out)."""
    cmd = [sys.executable, str(mutant_file), str(graph_file), start, end]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT
        )
        output = result.stdout.strip()
        if not output:
            output = result.stderr.strip() or "(no output)"
        return output, False
    except subprocess.TimeoutExpired:
        return "TIMEOUT", True
    except Exception as e:
        return f"ERROR: {e}", False


def parse_distance(output):
    """Extract float distance from 'Total distance: X' line, or None."""
    match = re.search(r"Total distance:\s*(-?inf|nan|[\d.]+)", output)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def run_mutant(mutant_id, meta):
    """
    Run one mutant across all MTGs.
    Returns list of row dicts (one per MTG, or one row if skipped).
    """
    n = mutant_id[1:]
    mutant_file = MUTANTS_DIR / f"mutant{n}.py"

    if meta.get("equivalent", False):
        print(f"  [{mutant_id}] SKIPPED (equivalent)")
        return [{
            "Mutant ID": mutant_id,
            "MTG ID": "",
            "Status": "Equivalent",
            "Notes": "Equivalent mutant - skipped",
            "Actual Output SI": "",
            "Actual Output FI1": "",
            "Actual Output FI2": "",
            "Actual Output Relation": "",
            "MR Verdict": "SKIPPED",
        }]

    rows = []
    mtg_verdicts = []

    for mtg_name, si_start, si_end, fi1_start, fi1_end, fi2_start, fi2_end in MTG_CONFIGS:
        si_path  = MR2_DIR / mtg_name / "SI.txt"
        fi1_path = MR2_DIR / mtg_name / "FI1.txt"
        fi2_path = MR2_DIR / mtg_name / "FI2.txt"

        si_out,  si_timeout  = run_cmd(mutant_file, si_path,  si_start,  si_end)
        fi1_out, fi1_timeout = run_cmd(mutant_file, fi1_path, fi1_start, fi1_end)
        fi2_out, fi2_timeout = run_cmd(mutant_file, fi2_path, fi2_start, fi2_end)

        if si_timeout or fi1_timeout or fi2_timeout:
            timed = [label for flag, label in [(si_timeout, "SI"), (fi1_timeout, "FI1"), (fi2_timeout, "FI2")] if flag]
            verdict = "TIMEOUT"
            relation = f"TIMEOUT - could not compare ({', '.join(timed)})"
            notes = f"Timed out on {', '.join(timed)}"
        else:
            si_dist  = parse_distance(si_out)
            fi1_dist = parse_distance(fi1_out)
            fi2_dist = parse_distance(fi2_out)

            if any(d is None for d in [si_dist, fi1_dist, fi2_dist]):
                verdict = "ERROR"
                relation = "ERROR - could not parse distance"
                notes = "Output did not contain a parseable distance"
            elif si_dist == fi1_dist + fi2_dist:
                verdict = "PASS"
                relation = "source distance == FI1 distance + FI2 distance"
                notes = f"SI={si_dist}, FI1={fi1_dist}, FI2={fi2_dist}"
            else:
                verdict = "FAIL"
                relation = "source distance \u2260 FI1 distance + FI2 distance"
                notes = f"SI={si_dist}, FI1={fi1_dist}, FI2={fi2_dist}"

        rows.append({
            "Mutant ID": mutant_id,
            "MTG ID": mtg_name,
            "Status": "Not Equivalent",
            "Notes": notes,
            "Actual Output SI": si_out,
            "Actual Output FI1": fi1_out,
            "Actual Output FI2": fi2_out,
            "Actual Output Relation": relation,
            "MR Verdict": verdict,
        })
        mtg_verdicts.append(verdict)

    if "TIMEOUT" in mtg_verdicts:
        summary = "TIMEOUT"
    elif "FAIL" in mtg_verdicts:
        failed = [MTG_CONFIGS[i][0] for i, v in enumerate(mtg_verdicts) if v == "FAIL"]
        summary = f"KILLED by {', '.join(failed)}"
    elif all(v == "ERROR" for v in mtg_verdicts):
        summary = "ERROR (all MTGs)"
    elif "ERROR" in mtg_verdicts:
        summary = "ERROR (some MTGs)"
    else:
        summary = "SURVIVED (all 5 MTGs passed)"

    print(f"  [{mutant_id}] {summary}")
    return rows


def main():
    meta = load_mutant_metadata()

    print("=" * 60)
    print("MR2 Mutation Testing — Subpath Optimality")
    print("=" * 60)

    all_rows = []
    for i in range(1, 46):
        mid = f"M{i}"
        m_meta = meta.get(mid, {})
        all_rows.extend(run_mutant(mid, m_meta))

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    killed_mutants = {r["Mutant ID"] for r in all_rows if r["MR Verdict"] == "FAIL"}
    survived_mutants = {r["Mutant ID"] for r in all_rows if r["MR Verdict"] == "PASS"} - killed_mutants
    timeout_mutants = {r["Mutant ID"] for r in all_rows if r["MR Verdict"] == "TIMEOUT"}
    skipped = len({r["Mutant ID"] for r in all_rows if r["MR Verdict"] == "SKIPPED"})

    print()
    print("=" * 60)
    print(f"Mutants KILLED  : {len(killed_mutants)}")
    print(f"Mutants SURVIVED: {len(survived_mutants)}")
    print(f"Mutants TIMEOUT : {len(timeout_mutants)}")
    print(f"Mutants SKIPPED : {skipped}")
    print(f"Output saved to : {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()
