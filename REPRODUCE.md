# Reproduce this yourself

Requirements: `curl`, `python3`, `pip`. No API keys, no accounts.

## 1. Read ESPN's dates straight from their API

```bash
for spec in nba/4278783 nba/4600663 wnba/5017605 wnba/4433744; do
  curl -s --max-time 25 "https://sports.core.api.espn.com/v2/sports/basketball/leagues/${spec%%/*}/athletes/${spec##*/}?lang=en" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['id'], d['displayName'], '->', d['dateOfBirth'])"
done
```

Expected (this is what ESPN serves right now):

```
4278783 Will Magnay -> 1998-07-10T07:00Z
4600663 Zach Edey -> 2002-03-14T08:00Z
5017605 Kamila Borkowska -> 2002-06-26T07:00Z
4433744 Michelle Onyiah -> 2003-03-12T08:00Z
```

## 2. Check the independent sources

Wikidata date of birth (P569), one call per player:

```bash
for q in Q65658814 Q106817973 Q106587773 Q119545957; do
  curl -s --max-time 25 "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=$q&property=P569&format=json" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('$q', '->', d['claims']['P569'][0]['mainsnak']['datavalue']['value']['time'])"
done
```

Expected:

```
Q65658814 -> +1998-06-10T00:00:00Z
Q106817973 -> +2002-05-14T00:00:00Z
Q106587773 -> +2002-07-26T00:00:00Z
Q119545957 -> +2002-03-12T00:00:00Z
```

Every one disagrees with ESPN. Same check on Basketball-Reference (open in a browser, DOB is at the top of the page):

- basketball-reference.com/players/m/magnawi01.html -> June 10, 1998
- basketball-reference.com/players/e/edeyza01.html -> May 14, 2002

NBA's own stats API, two ways. Direct endpoint (open in your browser):

- https://stats.nba.com/stats/commonplayerinfo?PlayerID=1630266&LeagueID=00 -> Will Magnay, BIRTHDATE 1998-06-10T00:00:00
- https://stats.nba.com/stats/commonplayerinfo?PlayerID=1641744&LeagueID=00 -> Zach Edey, BIRTHDATE 2002-05-14T00:00:00

(The endpoint bot-filters curl, so from a terminal use `pip install nba_api` instead:)

```bash
python3 -c "
from nba_api.stats.endpoints import commonplayerinfo
for pid in (1630266, 1641744):
    df = commonplayerinfo.CommonPlayerInfo(player_id=pid, timeout=30).get_data_frames()[0]
    print(pid, df['DISPLAY_FIRST_LAST'].iloc[0], '->', df['BIRTHDATE'].iloc[0])
"
```

Expected: `1630266 Will Magnay -> 1998-06-10T00:00:00`, `1641744 Zach Edey -> 2002-05-14T00:00:00`. (No stats-API bridge exists for WNBA players, which is why the WNBA cases rest on Wikidata plus the named independents in the verdicts table.)

## 3. Rebuild the dataset from scratch

```bash
python3 data/build_db.py
sqlite3 data/dob_mismatches.db "SELECT source, dob FROM dob_claims WHERE player_key='espn-4278783' ORDER BY dob, source;"
sqlite3 data/dob_mismatches.db "SELECT player_key, verdict, correct_dob FROM mismatch_verdicts;"
```

The build prints row counts (962 players, ~2700 claims, 6 verdicts). The first query shows the 7-vs-2 source split for Magnay; the second shows all six verdicts.

## What this proves and what it doesn't

Steps 1-2 prove ESPN serves these four dates and that independent sources disagree. They don't by themselves prove which side is right. That call lives in `data/mismatch_verdicts.csv`: a publisher is only marked wrong where 3+ independent sources agree, and the full per-source evidence is in `data/dob_claims.csv`.
