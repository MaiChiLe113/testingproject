"""
MR1 Mutation Testing Runner
Runs all 45 mutants against MR1 (Graph Transposition) test groups MTG1-MTG5.
MR1 property: |SP(G, a, b)| = |SP(G^T, b, a)|
Results are printed to terminal and saved to MR1_mutant_evaluation.csv.
Run from project root: python maichi/run_mr1_tests.py
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
MUTANTS_DIR = BASE / "MUTANTS"
MR1_DIR = BASE / "TEST" / "MR1"
MUTANT_CSV = BASE / "Mutant.csv"
OUTPUT_CSV = BASE / "MR1_mutant_evaluation.csv"
TIMEOUT = 10  # seconds

# (mtg_name, si_file, si_start, si_end, fi_file, fi_start, fi_end)
MTG_CONFIGS = [
    ("MTG1", "SI.txt", "A", "G",  "FI.txt", "G", "A"),
    ("MTG2", "SI.txt", "1", "6",  "FI.txt", "6", "1"),
    ("MTG3", "SI.txt", "P", "S",  "FI.txt", "S", "P"),
    ("MTG4", "SI.txt", "X", "V",  "FI.txt", "V", "X"),
    ("MTG5", "SI.txt", "S", "T",  "FI.txt", "T", "S"),
]

FIELDNAMES = [
    "Mutant ID",
    "MTG ID",
    "Status",
    "Notes",
    "Actual Output SI",
    "Actual Output FI",
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
            "Actual Output FI": "",
            "Actual Output Relation": "",
            "MR Verdict": "SKIPPED",
        }]

    rows = []
    mtg_verdicts = []

    for mtg_name, si_file, si_start, si_end, fi_file, fi_start, fi_end in MTG_CONFIGS:
        si_path = MR1_DIR / mtg_name / si_file
        fi_path = MR1_DIR / mtg_name / fi_file

        si_out, si_timeout = run_cmd(mutant_file, si_path, si_start, si_end)
        fi_out, fi_timeout = run_cmd(mutant_file, fi_path, fi_start, fi_end)

        if si_timeout or fi_timeout:
            verdict = "TIMEOUT"
            relation = "TIMEOUT - could not compare"
            notes = f"Timed out ({'SI' if si_timeout else 'FI'})"
        else:
            si_dist = parse_distance(si_out)
            fi_dist = parse_distance(fi_out)

            if si_dist is None or fi_dist is None:
                verdict = "ERROR"
                relation = "ERROR - could not parse distance"
                notes = "Output did not contain a parseable distance"
            elif si_dist == fi_dist:
                verdict = "PASS"
                relation = "source distance == follow-up distance"
                notes = f"SI={si_dist}, FI={fi_dist}"
            else:
                verdict = "FAIL"
                relation = "source distance \u2260 follow-up distance"
                notes = f"SI={si_dist}, FI={fi_dist}"

        rows.append({
            "Mutant ID": mutant_id,
            "MTG ID": mtg_name,
            "Status": "Not Equivalent",
            "Notes": notes,
            "Actual Output SI": si_out,
            "Actual Output FI": fi_out,
            "Actual Output Relation": relation,
            "MR Verdict": verdict,
        })
        mtg_verdicts.append(verdict)

    # Print per-mutant summary to terminal
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
    print("MR1 Mutation Testing — Graph Transposition")
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

    killed = sum(1 for r in all_rows if r["MR Verdict"] == "FAIL")
    survived_mutants = {
        r["Mutant ID"] for r in all_rows
        if r["MR Verdict"] == "PASS"
    }
    killed_mutants = {
        r["Mutant ID"] for r in all_rows
        if r["MR Verdict"] == "FAIL"
    }
    survived_only = survived_mutants - killed_mutants
    skipped = sum(1 for r in all_rows if r["MR Verdict"] == "SKIPPED")
    timeout = sum(1 for r in all_rows if r["MR Verdict"] == "TIMEOUT")

    print()
    print("=" * 60)
    print(f"Mutants KILLED : {len(killed_mutants)}")
    print(f"Mutants SURVIVED: {len(survived_only)}")
    print(f"Mutants TIMEOUT : {len({r['Mutant ID'] for r in all_rows if r['MR Verdict'] == 'TIMEOUT'})}")
    print(f"Mutants SKIPPED : {skipped}")
    print(f"Output saved to : {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()
