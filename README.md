# 4 wrong birth dates in ESPN's athlete API

I cross-validated player identity data across publishers for a research project. ESPN's `dateOfBirth` field is wrong for four players. Each one checks out against 6+ independent sources.

| Player | ESPN athlete ID | ESPN says | Real DOB |
|---|---|---|---|
| Will Magnay | 4278783 | 1998-07-10 | 1998-06-10 |
| Zach Edey | 4600663 | 2002-03-14 | 2002-05-14 |
| Kamila Borkowska | 5017605 | 2002-06-26 | 2002-07-26 |
| Michelle Onyiah | 4433744 | 2003-03-12 | 2002-03-12 |

## How they were caught

Every player got a 3-leg round trip: ESPN Core API, basketball-reference, and NBA stats. Any DOB disagreement quarantined the player instead of picking a side. Then each mismatch was verified against independent sources (Wikidata, Wikipedia, Basketball-Reference, RealGM, Sportradar, FIBA, official team pages). A publisher was only declared wrong at 3+ agreeing sources.

The wrong values aren't API glitches. For Magnay and Edey the same wrong date shows up on three separate ESPN surfaces (Core API, site API, team roster payloads), so it's in ESPN's underlying athlete record.

## What's not here

Two cases I checked and deliberately excluded: Johnny Furphy's DOB is genuinely split across sources (no verdict possible), and one apparent mismatch turned out to be Wikidata's error, not ESPN's. Both are documented in the full report.

## Full evidence

[DOB-MISMATCH-REPORT.md](DOB-MISMATCH-REPORT.md) has the per-player evidence tables, the verification sources, the pattern analysis, and the discovery methodology.

## Data

`data/` holds the relational dataset: `players.csv`, `dob_claims.csv` (every source's claimed DOB per player, the who-agrees-with-whom table), `mismatch_verdicts.csv`, `scans.csv`, plus `schema.sql`, `build_db.py`, and a prebuilt `dob_mismatches.db`. 962 players, ~2700 claims, 6 verdicts.

## Verify it yourself

[REPRODUCE.md](REPRODUCE.md): copy-paste commands that read ESPN's dates straight from their API, check the independent sources, and rebuild the dataset from scratch. No API keys needed.

---
Justin Poli, CS senior, SUNY New Paltz. Found something I got wrong? Open an issue.
