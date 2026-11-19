# SPDX-License-Identifier: Apache-2.0
# CP-SAT runs on the Phi_6 case around the fold proposition (vuza-canons 0.5.1).
# Part of vuza-canons. Made by MV2 of Munim, Inc., with AI agents.
# Licensed under the Apache License 2.0.
"""fold6sat: test the solver where the fold argument is silent.

foldlemma.py proves that a lift of S180 or C180 to Z_{180k} has no set
complement missing Phi_6 unless k = 5^s k' with k' >= 6. Two kinds of runs
follow from that:

  hard-negative  k = 6, 7, 8, 9 (M = 1080-1620). The fold argument allows a
                 Phi_6 failure, but Laba-Londner Cor. 6.2 forbids it (5 does
                 not divide |B| = 6k). Any verified FEASIBLE here contradicts a
                 published theorem, so it is a bug until proved otherwise. The
                 INFEASIBLE share measures whether CP-SAT can find the deeper
                 obstruction without the cheap one.
  frontier       k = 30 (M = 5400 = 2^3 3^3 5^2, sizes 30 / 180): the least
                 period where the proposition allows a Phi_6 failure, and no
                 published theorem covers T2 there. A verified FEASIBLE would be
                 a counterexample to the Coven-Meyerowitz T2 conjecture.

Pre-registered (2026-11-19, before any run):
  F1 every configuration finds a verified tiling (positive control);
  F2 no verified FEASIBLE Phi_6 case in a hard-negative configuration;
  F3 no verified FEASIBLE at the frontier (we expect UNKNOWN: the models are
     large);
  F4 the foldlemma checks reproduce fold_lemma.json inside the job.

Usage:
  python fold6sat.py --list
  python fold6sat.py --out-dir out --workers 2 --total-minutes 225
"""
import argparse
import json
import os
import sys
import time
import traceback

import foldlemma
import liftsat

VERSION = "0.5.1"

LL = "Laba-Londner Cor. 6.2 forbids it: 5 does not divide |B| = %d"
FRONT = "M = 5400 = 2^3 3^3 5^2, sizes 30 / 180: least period where the fold proposition allows a Phi_6 failure; no theorem covers it"

# name, source, q, k, label, seconds for the Phi_6 case, tile-control seconds, why
CONFIGS = [
    ("S180-k6", "S180", 1, 6, "hard-negative", 600, 60, "M=1080; " + LL % 36),
    ("C180-k6", "C180", 1, 6, "hard-negative", 600, 60, "M=1080; " + LL % 36),
    ("S180-k7", "S180", 1, 7, "hard-negative", 600, 60, "M=1260; " + LL % 42),
    ("S180-k8", "S180", 1, 8, "hard-negative", 600, 60, "M=1440; " + LL % 48),
    ("S180-k9", "S180", 1, 9, "hard-negative", 600, 60, "M=1620; " + LL % 54),
    ("S180-k30", "S180", 1, 30, "frontier", 3600, 300, FRONT),
    ("C180-k30", "C180", 1, 30, "frontier", 3600, 300, FRONT),
]


def configs():
    out = []
    for name, src, q, k, label, secs, tile_secs, why in CONFIGS:
        c = liftsat.config_dict((name, src, q, k, label, secs, why))
        c["tile_seconds"] = tile_secs
        out.append(c)
    return out


def cases(cfg):
    """The tile control and the B-side Phi_6 case of one configuration."""
    out = []
    for c in liftsat.config_cases(cfg):
        if c["mode"] == "tile" or (c["side"] == "B" and c["s"] == 6):
            out.append(c)
    return out


def plan():
    rows = []
    for c in configs():
        cs = cases(c)
        rows.append({"cfg": c["name"], "M": c["M"], "label": c["label"], "why": c["why"],
                     "profiles": [x["SA"] for x in cs if x["mode"] == "tile"],
                     "phi6_cases": len([x for x in cs if x["mode"] == "t2"]),
                     "decided": len([x for x in cs if x["decided"]])})
    return rows


def summarize(records, lemma_ok, meta):
    feas = ("FEASIBLE", "FEASIBLE_UNVERIFIED")
    t2 = [r for r in records if r["mode"] == "t2"]
    by = {}
    for r in records:
        P = by.setdefault(r["cfg"], {"label": r["label"], "M": r["M"], "tile": {}, "t2": {}})
        P[r["mode"]][r["status"]] = P[r["mode"]].get(r["status"], 0) + 1
    names = sorted({r["cfg"] for r in records})
    cands = [r for r in t2 if r["label"] == "frontier" and r["status"] == "FEASIBLE"]
    hard = [r for r in t2 if r["label"] == "hard-negative"]
    return {
        "version": VERSION, **meta,
        "per_config": by,
        "hard_negative_status": {st: sum(1 for r in hard if r["status"] == st) for st in sorted({r["status"] for r in hard})},
        "predictions": {
            "F1_every_config_has_a_verified_tiling": all(
                any(r["cfg"] == n and r["mode"] == "tile" and r["status"] == "FEASIBLE" for r in records)
                for n in names),
            "F2_no_feasible_phi6_case_in_hard_negatives": not any(r["status"] in feas for r in hard),
            "F3_no_verified_phi6_failure_at_5400": not cands,
            "F4_foldlemma_reproduces_fold_lemma_json": lemma_ok,
        },
        "bug_flags": {
            "unverified_feasible": sum(1 for r in records if r["status"] == "FEASIBLE_UNVERIFIED"),
            "model_invalid_or_error": sum(1 for r in records if r["status"] in ("MODEL_INVALID", "ERROR")),
            "theorem_violations": sum(1 for r in hard if r["status"] == "FEASIBLE"),
        },
        "T2_COUNTEREXAMPLE_CANDIDATES": len(cands),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--configs", default="", help="comma-separated config names (default: all)")
    ap.add_argument("--time-scale", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--total-minutes", type=float, default=225.0)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        print(json.dumps(plan(), indent=1))
        return 0

    os.makedirs(args.out_dir, exist_ok=True)
    doc = foldlemma.compute()
    with open(os.path.join(args.out_dir, "fold_lemma_computed.json"), "w") as f:
        json.dump(doc, f, indent=1)
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fold_lemma.json")) as f:
            lemma_ok = json.load(f) == doc
    except OSError:
        lemma_ok = False

    cfgs = configs()
    if args.configs:
        want = set(args.configs.split(","))
        cfgs = [c for c in cfgs if c["name"] in want]
    jpath = os.path.join(args.out_dir, "fold6_results.jsonl")
    spath = os.path.join(args.out_dir, "fold6_summary.json")
    cpath = os.path.join(args.out_dir, "T2_COUNTEREXAMPLE_CANDIDATES.json")
    with open(os.path.join(args.out_dir, "fold6_plan.json"), "w") as f:
        json.dump(plan(), f, indent=1)
    t0 = time.time()
    budget = args.total_minutes * 60.0
    records = []
    meta = {"workers": args.workers, "seed": args.seed, "time_scale": args.time_scale}

    def emit(rec):
        records.append(rec)
        with open(jpath, "a") as f:
            f.write(json.dumps(rec) + "\n")
        with open(spath, "w") as f:
            json.dump(summarize(records, lemma_ok, dict(meta, elapsed_s=round(time.time() - t0, 1))), f, indent=1)
        if rec["mode"] == "t2" and rec["status"] in ("FEASIBLE", "FEASIBLE_UNVERIFIED"):
            found = [r for r in records if r["mode"] == "t2" and r["status"] in ("FEASIBLE", "FEASIBLE_UNVERIFIED")]
            with open(cpath, "w") as f:
                json.dump(found, f, indent=1)
        print("%-9s %-4s M=%d -> %s (%.1fs)" % (rec["cfg"], rec["mode"], rec["M"], rec["status"],
                                                rec.get("wall", 0.0)), flush=True)

    print("fold6sat %s (foldlemma reproduces fold_lemma.json: %s)" % (VERSION, lemma_ok), flush=True)
    for c in cfgs:
        for case in cases(c):
            if case["decided"]:
                emit(dict(case, status="DECIDED_INFEASIBLE", wall=0.0))
                continue
            limit = c["tile_seconds"] if case["mode"] == "tile" else c["seconds"] * args.time_scale
            if time.time() - t0 > budget:
                emit(dict(case, status="SKIPPED_BUDGET", wall=0.0))
                continue
            try:
                rec = liftsat.solve_case(case, c, limit, args.workers, args.seed)
            except Exception:
                rec = dict(case, status="ERROR", wall=0.0, error=traceback.format_exc()[-2000:])
            emit(rec)
    doc = summarize(records, lemma_ok, dict(meta, elapsed_s=round(time.time() - t0, 1), finished=True))
    with open(spath, "w") as f:
        json.dump(doc, f, indent=1)
    print(json.dumps(doc["predictions"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
