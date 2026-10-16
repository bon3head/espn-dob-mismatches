#!/usr/bin/env python3
"""Assign standard-time UTC offset per player from Wikidata P19 place+country+coords.
Writes offsets.json: {qid: {offset, place, country, method}}.
Caveats: DST ignored (standard time per task); longitude-band heuristics for
multi-zone countries; reviewed manually for mismatches and stratified sample."""
import json, re, collections

OUT = "/home/hatch/workspace/nba-player-track/reports/dob-investigation/timezone-scan"
bp = json.load(open(f"{OUT}/birthplaces.json"))

COUNTRY_OFFSET = {
    "France": 1, "Spain": 1, "Germany": 1, "Serbia": 1, "Nigeria": 1,
    "Switzerland": 1, "Italy": 1, "Belgium": 1, "Bosnia and Herzegovina": 1,
    "Cameroon": 1, "United Kingdom": 0, "Sweden": 1, "Netherlands": 1,
    "South Africa": 2, "Greece": 2, "Lithuania": 2, "Latvia": 2, "Finland": 2,
    "Ukraine": 2, "Turkey": 3, "Israel": 2, "South Sudan": 2, "Sudan": 2,
    "Guinea": 0, "Senegal": 0, "The Bahamas": -5, "Japan": 9,
    "People's Republic of China": 8, "New Zealand": 12, "Slovenia": 1,
    "Croatia": 1, "Czech Republic": 1, "North Macedonia": 1, "Uzbekistan": 5,
    "Haiti": -5, "Austria": 1, "Mali": 0, "Argentina": -3, "Georgia": 4,
    "Republic of the Congo": 1, "Roman Empire": 1, "Saint Lucia": -4,
    "Jamaica": -5, "Angola": 1, "Dominican Republic": -4, "Montenegro": 1,
    "Portugal": 0,
}

def lon_of(rec):
    m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", rec.get("coord") or "")
    return float(m.group(1)) if m else None

def multi_zone(country, lon):
    if lon is None:
        return None
    if country in ("United States", "Ohio"):  # Ohio appears as 'country' for one record
        if lon >= -67.5: return -4    # PR, USVI (AST)
        if lon >= -85: return -5      # Eastern
        if lon >= -102: return -6     # Central (incl. all of TX/OK)
        if lon >= -114: return -7     # Mountain
        if lon >= -125: return -8     # Pacific
        if lon >= -150: return -9     # Alaska
        return -10                    # Hawaii
    if country == "Canada":
        if lon >= -60: return -4      # Atlantic (fold -3:30 Nfld into -4 bucket)
        if lon >= -95: return -5      # Eastern incl. western Ontario
        if lon >= -110: return -6     # Central
        if lon >= -120: return -7     # Mountain (BC/AB border)
        if lon >= -140: return -8     # Pacific
        return -9
    if country == "Australia":
        if lon >= 141: return 10
        if lon >= 129: return 9.5
        return 8
    if country == "Brazil":
        if lon >= -50: return -3   # BRT incl. southeast + DF
        if lon >= -60: return -4   # AMT
        return -5
    if country == "Russia":
        return round(lon / 15)
    if country == "Democratic Republic of the Congo":
        return 2 if lon >= 25 else 1
    return None

out, unmatched = {}, []
for q, r in bp.items():
    c = r.get("countryLabel")
    lon = lon_of(r)
    off, method = None, None
    if c in COUNTRY_OFFSET:
        off, method = COUNTRY_OFFSET[c], "country"
    elif c in ("United States", "Ohio", "Canada", "Australia", "Brazil", "Russia",
               "Democratic Republic of the Congo"):
        off, method = multi_zone(c, lon), "country+lon"
    if off is None:
        unmatched.append((q, c, r.get("pobLabel")))
    out[q] = {"offset": off, "place": r.get("pobLabel"),
              "country": c, "lon": lon, "method": method}

json.dump(out, open(f"{OUT}/offsets.json", "w"), indent=1)
print("assigned:", sum(1 for v in out.values() if v["offset"] is not None),
      "unmatched:", len(unmatched))
for u in unmatched:
    print("UNMATCHED:", u)
dist = collections.Counter(v["offset"] for v in out.values() if v["offset"] is not None)
print("offset distribution:", dict(sorted(dist.items())))
