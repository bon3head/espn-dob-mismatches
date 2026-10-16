#!/usr/bin/env python3
"""Timezone-correlation analysis for the DOB mismatch scan.
Corpus-wide mismatch rate per |offset| bucket + Fisher exact tests."""
import json, collections, math
from datetime import date

OUT = "/home/hatch/workspace/nba-player-track/reports/dob-investigation/timezone-scan"
off = json.load(open(f"{OUT}/offsets.json"))
rows = [json.loads(l) for l in open(
    "/home/hatch/workspace/nba-player-track/curated/build-2026-10-15/roundtrip_log.jsonl")]
by_qid = {r["qid"]: r for r in rows}

def day_delta(r):
    e = date.fromisoformat(r["espn_dob_date"])
    n = date.fromisoformat(r["nba_dob_date"])
    return (e - n).days  # positive => ESPN later

print("=== mismatch direction analysis ===")
for r in rows:
    if r["dob_match"] is False:
        o = off[r["qid"]]
        d = day_delta(r)
        print(f"espn {r['espn']} ({o['place']}, UTC{o['offset']:+}): "
              f"ESPN {r['espn_dob_date']} vs NBA {r['nba_dob_date']} => delta {d:+d} days "
              f"(ESPN {'later' if d > 0 else 'earlier'})")

print("\n=== corpus mismatch rate by |offset| ===")
tot = collections.Counter()
mm = collections.Counter()
for q, o in off.items():
    a = abs(o["offset"])
    tot[a] += 1
    if by_qid[q]["dob_match"] is False:
        mm[a] += 1
for a in sorted(tot):
    print(f"|offset|={a:>5}: {mm[a]}/{tot[a]} mismatches ({100*mm[a]/tot[a]:.2f}%)")

def fisher_exact(a, b, c, d):
    from math import comb
    n1, n2, m1 = a + b, c + d, a + c
    N = n1 + n2
    p = 0.0
    for x in range(a, min(n1, m1) + 1):
        p += comb(n1, x) * comb(n2, m1 - x) / comb(N, m1)
    return p

a1 = sum(mm[a] for a in mm if a >= 9); b1 = sum(tot[a] for a in tot if a >= 9) - a1
c1 = sum(mm[a] for a in mm if a < 9);  d1 = sum(tot[a] for a in tot if a < 9) - c1
print(f"\nTest1 all-mismatch [[{a1},{b1}],[{c1},{d1}]] Fisher p = {fisher_exact(a1,b1,c1,d1):.4f}")

mm_day = collections.Counter()
for r in rows:
    if r["dob_match"] is False and abs(day_delta(r)) == 1:
        mm_day[abs(off[r["qid"]]["offset"])] += 1
a2 = sum(mm_day[a] for a in mm_day if a >= 9); b2 = sum(tot[a] for a in tot if a >= 9) - a2
c2 = sum(mm_day[a] for a in mm_day if a < 9);  d2 = sum(tot[a] for a in tot if a < 9) - c2
print(f"Test2 day-level [[{a2},{b2}],[{c2},{d2}]] Fisher p = {fisher_exact(a2,b2,c2,d2):.4f}")
