#!/usr/bin/env python3
"""Fetch Wikidata P19 (place of birth) + labels + coordinates + country for all corpus QIDs.
Read-only on sprint files. Polite WDQS: 50 ids/batch, >=1s spacing, contact UA, 3 attempts."""
import json, time, os, sys

try:
    import requests
except ImportError:
    sys.exit("requests needed")

BUILD_DIR = "/home/hatch/workspace/nba-player-track/curated/build-2026-10-15"
OUT_DIR = "/home/hatch/workspace/nba-player-track/reports/dob-investigation/timezone-scan"
UA = "CipherXwalk/1.0 (nba-player-track research build; https://www.wikidata.org)"
ENDPOINT = "https://query.wikidata.org/sparql"
os.makedirs(OUT_DIR, exist_ok=True)

def chunk(ids, n=50):
    for i in range(0, len(ids), n):
        yield ids[i:i+n]

def build_query(qids):
    vals = " ".join("wd:%s" % q for q in qids)
    return (
        "SELECT ?p ?pob ?pobLabel ?coord ?country ?countryLabel WHERE {\n"
        "  VALUES ?p { " + vals + " }\n"
        "  OPTIONAL { ?p wdt:P19 ?pob .\n"
        "    OPTIONAL { ?pob wdt:P625 ?coord. }\n"
        "    OPTIONAL { ?pob wdt:P17 ?country. } }\n"
        '  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }\n'
        "}"
    )

def fetch(query):
    last = None
    for attempt in range(1, 4):
        try:
            r = requests.get(ENDPOINT, params={"query": query, "format": "json"},
                             headers={"User-Agent": UA, "Accept": "application/sparql-results+json"},
                             timeout=120)
            r.raise_for_status()
            return json.loads(r.content)
        except Exception as e:
            last = "%s: %s" % (type(e).__name__, e)
            time.sleep(5 * attempt)
    raise RuntimeError("SPARQL failed: %s" % last)

def main():
    rows = [json.loads(l) for l in open(os.path.join(BUILD_DIR, "roundtrip_log.jsonl"))]
    qids = sorted({r["qid"] for r in rows if r.get("qid")})
    print("QIDs:", len(qids), flush=True)
    out = {}
    for bi, batch in enumerate(chunk(qids)):
        data = fetch(build_query(batch))
        for b in data["results"]["bindings"]:
            q = b["p"]["value"].rsplit("/", 1)[-1]
            rec = out.setdefault(q, {"qid": q, "pob": None, "pobLabel": None,
                                     "coord": None, "country": None, "countryLabel": None})
            if "pob" in b:
                rec["pob"] = b["pob"]["value"].rsplit("/", 1)[-1]
                rec["pobLabel"] = b.get("pobLabel", {}).get("value")
            if "coord" in b:
                rec["coord"] = b["coord"]["value"]  # "Point(lon lat)"
            if "country" in b:
                rec["country"] = b["country"]["value"].rsplit("/", 1)[-1]
                rec["countryLabel"] = b.get("countryLabel", {}).get("value")
        print("batch %d/%d done" % (bi + 1, (len(qids) + 49) // 50), flush=True)
        time.sleep(1.0)
    json.dump(out, open(os.path.join(OUT_DIR, "birthplaces.json"), "w"), indent=1)
    missing = [q for q, r in out.items() if not r["pob"]]
    print("saved. total:", len(out), "missing P19:", len(missing))

if __name__ == "__main__":
    main()
