# Timezone-Stratified DOB Scan — Findings

Extension of the DOB mismatch investigation. Tests whether DOB disagreements
between ESPN and NBA stats correlate with birthplace UTC offset (the
UTC-vs-local-time artifact hypothesis, motivated by the Furphy case: ESPN one
day earlier than NBA for a Melbourne-born player).

Scan date: 2026-10-15. All sprint files read-only; nothing modified.

## Method

1. **Birthplaces:** Wikidata P19 (place of birth) + coordinates + country for
   all 741 corpus QIDs via WDQS, 50/batch (`fetch_birthplaces.py`). 741/741
   resolved, 0 missing.
2. **Offset assignment:** standard-time UTC offset per birthplace
   (`assign_offsets.py`). Single-zone countries mapped directly; multi-zone
   countries (US, Canada, Australia, Brazil, Russia, DRC) via longitude bands.
   DST ignored per task spec. Three boundary bugs were found and fixed during
   review: US Central/Mountain (-97.5 → -102, misclassified San Antonio,
   Oklahoma City, Killeen), Canada Mountain/Pacific (-125 → -120,
   misclassified Vancouver), Brazil BRT/AMT (-45 → -50, misclassified
   Brasília and São Paulo-state municipalities). All assignments re-verified
   after fixes.
3. **Stratified list:** 61 players, 3–5 per covered bucket (all available
   where < 3), deterministic by espn_id, all 3 known mismatches pinned into
   their buckets (`build_sample.py` → `stratified_list.json`). Corpus legs
   (espn_leg.dob, nba_leg.birthdate, dob_match) reused from
   `roundtrip_log.jsonl` — no new fetches needed for corpus players.
4. **Zone-fill attempts:** uncovered zones (UTC-10, -9, +5:30, +6, +7, +11)
   probed for outside-corpus NBA players with the three ID keys (3-attempt
   cap each).
5. **Analysis:** mismatch rate per |offset| bucket, per-mismatch direction
   (signed day delta), Fisher exact tests (`analyze.py` → `analysis.json`).

## Stratified list (61 players, 17 buckets)

| espn_id | UTC offset | Birthplace | ESPN DOB | NBA DOB | Match |
|---|---|---|---|---|---|
| 2011 | -8 | Lakewood, United States | 1981-03-17 | 1981-03-17 | True |
| 2797 | -8 | Bremerton, United States | 1986-06-19 | 1986-06-19 | True |
| 3447 | -8 | North Hollywood, United States | 1988-04-01 | 1988-04-01 | True |
| 3448 | -8 | North Hollywood, United States | 1988-04-01 | 1988-04-01 | True |
| 3449 | -8 | Santa Monica, United States | 1988-09-07 | 1988-09-07 | True |
| 3999 | -7 | Cheyenne, United States | 1987-02-20 | 1987-02-20 | True |
| 3078576 | -7 | Parker, United States | 1994-07-02 | 1994-07-02 | True |
| 3907498 | -7 | Scottsdale, United States | 1997-03-04 | 1997-03-04 | True |
| 3908845 | -7 | Layton, United States | 1997-09-23 | 1997-09-23 | True |
| 4066757 | -7 | Bountiful, United States | 1996-05-15 | 1996-05-15 | True |
| 2386 | -6 | Springfield, United States | 1984-01-28 | 1984-01-28 | True |
| 2778 | -6 | Dallas, United States | 1987-03-18 | 1987-03-18 | True |
| 2799 | -6 | Memphis, United States | 1986-10-27 | 1986-10-27 | True |
| 2983 | -6 | Dallas, United States | 1985-07-19 | 1985-07-19 | True |
| 3015 | -6 | Monroe, United States | 1985-02-10 | 1985-02-10 | True |
| 1966 | -5 | Akron, United States | 1984-12-30 | 1984-12-30 | True |
| 1975 | -5 | Brooklyn, United States | 1984-05-29 | 1984-05-29 | True |
| 2384 | -5 | Atlanta, United States | 1985-12-08 | 1985-12-08 | True |
| 2426 | -5 | Miami, United States | 1985-06-30 | 1985-06-30 | True |
| 4600663 | -5 | Toronto, Canada | 2002-03-14 | 2002-05-14 | **False** |
| 3055 | -4 | Mayagüez, United States | 1984-06-26 | 1984-06-26 | True |
| 3213 | -4 | Luperon pto pta, Dominican Republic | 1986-06-03 | 1986-06-03 | True |
| 3948153 | -4 | Castries, Saint Lucia | 1993-01-11 | 1993-01-11 | True |
| 2968334 | -3 | Córdoba, Argentina | 1991-03-23 | 1991-03-23 | True |
| 2968361 | -3 | Belo Horizonte, Brazil | 1992-05-19 | 1992-05-19 | True |
| 3113297 | -3 | Q4035, Brazil | 1995-09-21 | 1995-09-21 | True |
| 4997536 | -3 | Brasília, Brazil | 2002-06-22 | 2002-06-22 | True |
| 2534781 | +0 | Kébémer, Senegal | 1990-01-18 | 1990-01-18 | True |
| 3904625 | +0 | Dakar, Senegal | 1995-12-10 | 1995-12-10 | True |
| 3918423 | +0 | St Mary's Hospital, United Kingdom | 1997-03-30 | 1997-03-30 | True |
| 3919335 | +0 | Kayes, Mali | 1996-09-13 | 1996-09-13 | True |
| 3934719 | +0 | London, United Kingdom | 1997-07-17 | 1997-07-17 | True |
| 2774 | +1 | Rouen, France | 1986-11-05 | 1986-11-05 | True |
| 3206 | +1 | Barcelona, Spain | 1985-01-29 | 1985-01-29 | True |
| 3416 | +1 | Lisieux, France | 1988-12-14 | 1988-12-14 | True |
| 3423 | +1 | Ljubljana, Slovenia | 1986-05-06 | 1986-05-06 | True |
| 3428 | +1 | Sant'Angelo Lodigiano, Italy | 1988-08-08 | 1988-08-08 | True |
| 6426 | +2 | Valmiera, Latvia | 1992-11-12 | 1992-11-12 | True |
| 6427 | +2 | Lubumbashi, Democratic Republic of the Congo | 1992-08-28 | 1992-08-28 | True |
| 6477 | +2 | Utena, Lithuania | 1992-05-06 | 1992-05-06 | True |
| 2596107 | +2 | Antratsyt, Ukraine | 1993-06-16 | 1993-06-16 | True |
| 3032977 | +2 | Athens, Greece | 1994-12-06 | 1994-12-06 | True |
| 2767 | +3 | Eskişehir, Turkey | 1987-05-15 | 1987-05-15 | True |
| 3929325 | +3 | Istanbul, Turkey | 1997-07-24 | 1997-07-24 | True |
| 4871144 | +3 | Giresun, Turkey | 2002-07-25 | 2002-07-25 | True |
| 5175643 | +3 | Moscow, Russia | 2006-03-03 | 2006-03-03 | True |
| 4348700 | +4 | Sagarejo, Georgia | 1999-07-20 | 1999-07-20 | True |
| 3074213 | +5 | Tashkent, Uzbekistan | 1998-06-19 | 1998-06-19 | True |
| 5217746 | +8 | Zibo, People's Republic of China | 2005-06-26 | 2005-06-26 | True |
| 3133838 | +9 | Yokohama, Japan | 1994-10-13 | 1994-10-13 | True |
| 4066648 | +9 | Toyama, Japan | 1998-02-08 | 1998-02-08 | True |
| 4432174 | +9 | Yokosuka, Japan | 2001-10-13 | 2001-10-13 | True |
| 5159895 | +9 | Yanai, Japan | 2001-05-02 | 2001-05-02 | True |
| 2968436 | +9.5 | Adelaide, Australia | 1987-10-02 | 1987-10-02 | True |
| 4004 | +10 | Canberra, Australia | 1988-08-11 | 1988-08-11 | True |
| 6442 | +10 | Melbourne, Australia | 1992-03-23 | 1992-03-23 | True |
| 2489693 | +10 | Frankston, Australia | 1990-08-23 | 1990-08-23 | True |
| 4278783 | +10 | Brisbane, Australia | 1998-07-10 | 1998-06-10 | **False** |
| 5157066 | +10 | Melbourne, Australia | 2004-12-07 | 2004-12-08 | **False** |
| 2968439 | +12 | Gisborne, New Zealand | 1986-12-09 | 1986-12-09 | True |
| 2991235 | +12 | Rotorua, New Zealand | 1993-07-20 | 1993-07-20 | True |

(Birthplace labels are Wikidata P19 as returned; "Q4035" is a São Paulo-state
municipality whose English label is absent in Wikidata.)

## Zone-fill attempts (outside corpus)

| Zone | Attempt | Outcome |
|---|---|---|
| UTC-10 | Searched for NBA players born in Hawaii (3-attempt equivalent: web search for Hawaii-born NBA players with ESPN/NBA-stats/bbref keys) | **Uncovered.** Hawaii-born pros found (Freddie Lish, Hugh Watanabe) lack NBA legs. |
| UTC+5:30 | Satnam Singh (Baloke, Punjab, India). Attempt 1: ESPN Core API search param — endpoint ignores it. Attempt 2: web search — found bbref `singhsa01`, no ESPN athlete ID. Attempt 3: tried G League ID 1626228 as ESPN ID — HTTP fail. NBA-stats leg impossible (never played an NBA regular-season game). | **Uncovered** (IDs unresolvable per 3-attempt cap). |
| UTC+11 | No known NBA player from +11 zone (Solomon Islands/Vanuatu/New Caledonia) | **Uncovered.** |
| UTC+6 / +7 | No known NBA player from these zones | **Uncovered.** |
| UTC-9 | No corpus player; no candidate pursued (Alaska/Yukon, none known) | **Uncovered.** |

## Corpus-wide mismatch rate per |offset| bucket

| |offset| | Mismatches / players | Rate |
|---|---|---|
| 0 | 0/9 | 0.00% |
| 1 | 0/87 | 0.00% |
| 2 | 0/21 | 0.00% |
| 3 | 0/8 | 0.00% |
| 4 | 0/4 | 0.00% |
| 5 | 1/277 | 0.36% |
| 6 | 0/208 | 0.00% |
| 7 | 0/11 | 0.00% |
| 8 | 0/96 | 0.00% |
| 9 | 0/4 | 0.00% |
| 9.5 | 0/1 | 0.00% |
| 10 | 2/13 | 15.38% |
| 12 | 0/2 | 0.00% |

Corpus total: 3/741 (0.40%).

## Direction analysis (signed ESPN-minus-NBA day deltas)

| Player | Birthplace (UTC) | ESPN | NBA | Delta | ESPN side |
|---|---|---|---|---|---|
| Magnay | Brisbane (+10) | 1998-07-10 | 1998-06-10 | +30d | later |
| Edey | Toronto (-5) | 2002-03-14 | 2002-05-14 | -61d | earlier |
| Furphy | Melbourne (+10) | 2004-12-07 | 2004-12-08 | -1d | earlier |

If the mechanism were "ESPN stores the UTC-normalized date, NBA stores the
local date", positive-offset birthplaces should show ESPN *earlier* and
negative-offset birthplaces ESPN *later*. Furphy (UTC+10, ESPN earlier) fits;
Magnay (UTC+10, ESPN *later* by 30 days) contradicts it; Edey (UTC-5, ESPN
earlier by 61 days) contradicts it. Direction kills the TZ mechanism for 2
of 3 cases outright.

## The explicit test: do day-level disagreements cluster at large |offset|?

- Test 1 (all 3 mismatches, |offset|≥9 vs <9): table [[2,18],[1,720]],
  Fisher exact p = 0.0020.
- Test 2 (day-level only — the only class a TZ artifact can produce):
  table [[1,19],[0,721]], Fisher exact p = 0.0270.

Both p-values are **post-hoc** (the hypothesis was formed after observing
2/3 mismatches at UTC+10) and must be read as descriptive, not confirmatory.
Test 1 is additionally confounded: it counts Magnay's +30d month-level error,
which cannot be a timezone artifact under any mechanism, so the "significant
clustering" is a statistical mirage for the TZ hypothesis — the cluster is
real as a raw fact (2/13 at |10| vs 1/728 elsewhere) but its driver is not
timezone. Test 2 rests on a single observation (Furphy) and cannot confirm
or refute anything.

## Verdict on the timezone-artifact hypothesis

| Claim | Verdict | Confidence |
|---|---|---|
| DOB disagreements in general are UTC-vs-local artifacts | **KILLED** | HIGH — 2 of 3 mismatches are month-level (30d, 61d); directions contradict UTC-normalization for 2 of 3 |
| Day-level ambiguity (Furphy pattern) arises from UTC-vs-local at large offsets | **UNRESOLVED** | LOW — exactly one supporting data point; direction consistent (ESPN earlier at UTC+10) but n=1; independent sources split 9-5 |
| Mismatches cluster at \|offset\|=10 as a raw statistical fact | Observed | MODERATE — 2/13 (15.4%) vs 1/728 (0.14%) elsewhere, p=0.002 post-hoc; mechanism unknown, not timezone for the month-level case |

The |10| bucket is the one place in the corpus where mismatches concentrate,
and it contains the only day-level case. That makes it the highest-priority
bucket for the re-run monitor, but it does not rehabilitate the timezone
mechanism: the bucket's other mismatch (Magnay) is a month-level record
error, proven ESPN-at-fault by 9 independent sources.

## Files

- `stratified_list.json` — the 61-player list (ID keys, birthplace, offset, both DOB legs, match flag)
- `analysis.json` — bucket rates, per-mismatch deltas, test tables
- `offsets.json` — UTC offset per QID with place/country/method
- `birthplaces.json` — raw Wikidata P19 payload per QID
- `fetch_birthplaces.py`, `assign_offsets.py`, `build_sample.py`, `analyze.py` — the pipeline
- `FINDINGS.md` — this file
