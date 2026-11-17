# SPDX-License-Identifier: Apache-2.0
# Run the pre-registered case list. Made by MV2 of Munim, Inc., with AI agents.
"""Usage: python run_cases.py --out-dir /out [--case-minutes 12] [--total-minutes 330]

Parameters use Jedrzejewski's order (n1, p1, n2, p2, n3); N = n1 p1 n2 p2 n3.
'published' is the number of aperiodic complements (up to translation) of the
standard outer rhythm reported by Auricchio, Ferrarini, Gualandi and Pernazza
(arXiv 2112.05249, Tables 1-2; their column order is p1, n1, p2, n2, n3).
"""
import argparse
import json
import os
import sys
import time

import vuza

# group, params, published aperiodic complement count (None = not published)
CASES = [
    # 1. validation against published complete counts
    ("validate", (2, 2, 3, 3, 2), 6),
    ("validate", (2, 2, 3, 3, 3), 252),
    ("validate", (2, 2, 3, 5, 2), 18),
    ("validate", (2, 2, 5, 3, 2), 20),
    ("validate", (2, 2, 3, 7, 2), 54),
    ("validate", (2, 2, 7, 3, 2), 42),
    ("validate", (2, 2, 3, 5, 3), 2052),
    ("validate", (2, 2, 5, 3, 3), 1800),
    ("validate", (3, 3, 2, 5, 2), 96),
    ("validate", (5, 2, 3, 3, 2), 120),
    # 2. N = 420 = 2^2*3*5*7 (four primes, outside the p^2 q^2 r^2 theorem);
    #    these six have |R| with three distinct primes, so T2 is not automatic
    ("n420-t2", (5, 7, 2, 3, 2), 720),
    ("n420-t2", (7, 5, 2, 3, 2), 672),
    ("n420-t2", (3, 7, 2, 5, 2), 864),
    ("n420-t2", (7, 3, 2, 5, 2), 6720),
    ("n420-t2", (2, 7, 3, 5, 2), 1872),
    ("n420-t2", (2, 7, 5, 3, 2), 22320),
    # 3. new periods (no published complete enumeration found); |R| has three
    #    distinct primes and N is not covered by the p^2 q^2 r^2 theorem
    ("new", (4, 2, 3, 5, 3), None),   # 360 = 2^3 3^2 5, |R| = 30
    ("new", (4, 2, 3, 7, 3), None),   # 504 = 2^3 3^2 7, |R| = 42
    ("new", (2, 2, 9, 5, 3), None),   # 540 = 2^2 3^3 5, |R| = 30
    ("new", (7, 5, 3, 3, 2), None),   # 630 = 2 3^2 5 7, |R| = 30
    ("new", (3, 3, 7, 5, 2), None),   # 630, |R| = 30
    ("new", (5, 11, 2, 3, 2), None),  # 660 = 2^2 3 5 11, |R| = 66
    ("new", (11, 5, 2, 3, 2), None),  # 660, |R| = 30
    ("new", (7, 11, 2, 3, 2), None),  # 924 = 2^2 3 7 11, |R| = 66
    ("new", (11, 7, 2, 3, 2), None),  # 924, |R| = 42
    # 4. remaining N = 420 cases (|R| with two primes: T2 automatic; validation)
    ("n420-val", (5, 7, 3, 2, 2), 3120),
    ("n420-val", (7, 5, 3, 2, 2), 1008),
    ("n420-val", (3, 7, 5, 2, 2), 33480),
    ("n420-val", (7, 3, 5, 2, 2), 840),
    ("n420-val", (7, 2, 3, 5, 2), 10080),
    ("n420-val", (7, 2, 5, 3, 2), 1120),
    # 5. heavier cases last
    ("new", (4, 2, 5, 3, 5), None),   # 600 = 2^3 3 5^2, |R| = 30
    ("new", (5, 7, 2, 3, 4), None),   # 840 = 2^3 3 5 7, |R| = 84
    ("validate", (2, 2, 3, 3, 4), 8640),
    ("validate", (2, 2, 3, 3, 5), 281232),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--case-minutes", type=float, default=12.0)
    ap.add_argument("--total-minutes", type=float, default=330.0)
    ap.add_argument("--only", default="", help="comma list of groups")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    t_start = time.time()
    results = []
    meta = {"version": vuza.VERSION, "numpy": vuza._np is not None, "python": sys.version.split()[0],
            "case_minutes": args.case_minutes, "total_minutes": args.total_minutes}
    groups = set(g for g in args.only.split(",") if g)
    wav_done = set()
    for group, params, published in CASES:
        if groups and group not in groups:
            continue
        left = args.total_minutes * 60 - (time.time() - t_start)
        if left < 60:
            results.append({"group": group, "params": params, "skipped": "total time budget used"})
            continue
        N, S = vuza.vuza_outer(*params)
        print("case", group, params, "N =", N, "|S| =", len(S), flush=True)
        res = vuza.analyze_case(S, N, time_limit=min(args.case_minutes * 60, left - 30))
        res.update({"group": group, "params": list(params), "params_order": "n1,p1,n2,p2,n3",
                    "published_aperiodic": published})
        if published is not None and res["complete"]:
            res["matches_published"] = res["aperiodic_classes"] == published
        _, Rstd = vuza.vuza_inner(*params)
        res["standard_inner"] = Rstd
        res["standard_inner_tiles"] = vuza.is_tiling(S, Rstd, N)
        res["standard_inner_periodic"] = vuza.is_periodic(Rstd, N)
        # one audio rendering per new period: the first aperiodic complement found
        if group == "new" and N not in wav_done and res["aperiodic_examples"]:
            R = res["aperiodic_examples"][0]
            path = os.path.join(args.out_dir, "canon_%d_%s.wav" % (N, "-".join(map(str, params))))
            try:
                res["wav_seconds"] = round(vuza.render_canon_wav(path, S, R, N, cycles=2), 1)
                res["wav"] = os.path.basename(path)
                wav_done.add(N)
            except Exception as e:  # audio is a bonus; never lose results for it
                res["wav_error"] = repr(e)
        print(json.dumps({k: res[k] for k in ("N", "complete", "seconds", "classes", "aperiodic_classes",
                                              "t1_failures", "t2_failure_classes", "translates_consistent")}),
              flush=True)
        results.append(res)
        with open(os.path.join(args.out_dir, "results.json"), "w") as f:
            json.dump({"meta": meta, "results": results}, f, indent=1)
    summary = []
    for r in results:
        if "skipped" in r:
            summary.append({"params": r["params"], "skipped": r["skipped"]})
            continue
        summary.append({k: r.get(k) for k in ("group", "params", "N", "size_S", "size_R", "complete", "seconds",
                                              "classes", "aperiodic_classes", "aperiodic_classes_mod_reflection",
                                              "published_aperiodic", "matches_published", "t1_failures",
                                              "t2_failure_classes", "aperiodic_t2_failure_classes",
                                              "R_has_3plus_primes", "translates_consistent")})
    meta["elapsed_minutes"] = round((time.time() - t_start) / 60, 1)
    with open(os.path.join(args.out_dir, "summary.json"), "w") as f:
        json.dump({"meta": meta, "summary": summary}, f, indent=1)
    with open(os.path.join(args.out_dir, "results.json"), "w") as f:
        json.dump({"meta": meta, "results": results}, f, indent=1)
    bad = [r for r in results if r.get("t1_failures")
           or (r.get("complete") and r.get("translates_consistent") is False)]
    if bad:
        print("SANITY FAILURE: T1 failed or translate count inconsistent in", [r["params"] for r in bad])
    print("done in", meta["elapsed_minutes"], "minutes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
