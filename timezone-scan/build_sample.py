#!/usr/bin/env python3
"""Build the timezone-stratified player list from the corpus.
Deterministic: within each bucket, sort by espn id; always include mismatches.
Writes stratified_list.json."""
import json, collections

OUT = "/home/hatch/workspace/nba-player-track/reports/dob-investigation/timezone-scan"
off = json.load(open(f"{OUT}/offsets.json"))
rows = [json.loads(l) for l in open(
    "/home/hatch/workspace/nba-player-track/curated/build-2026-10-15/roundtrip_log.jsonl")]
by_qid = {r["qid"]: r for r in rows}

buckets = collections.defaultdict(list)
for q, o in off.items():
    buckets[o["offset"]].append(q)

mismatch_qids = {r["qid"] for r in rows if r["dob_match"] is False}

sample = []
for b in sorted(buckets):
    qs = sorted(buckets[b], key=lambda q: by_qid[q]["espn"])
    pinned = [q for q in qs if q in mismatch_qids]
    rest = [q for q in qs if q not in mismatch_qids]
    chosen = pinned + rest[: max(0, 5 - len(pinned))]
    for q in chosen:
        r = by_qid[q]
        o = off[q]
        sample.append({
            "espn_id": r["espn"], "nba_id": r["nba_id"], "bbref": r["bbref"],
            "qid": q, "birthplace": o["place"], "country": o["country"],
            "utc_offset": o["offset"], "in_corpus": True,
            "espn_dob_date": r["espn_dob_date"], "nba_dob_date": r["nba_dob_date"],
            "dob_match": r["dob_match"],
            "mismatch": r["dob_match"] is False,
        })

json.dump(sample, open(f"{OUT}/stratified_list.json", "w"), indent=1)
per_bucket = collections.Counter(s["utc_offset"] for s in sample)
print("sample size:", len(sample))
print("per bucket:", dict(sorted(per_bucket.items())))
print("mismatches in sample:", sum(1 for s in sample if s["mismatch"]))
