# DOB Mismatch Investigation Report

Independent investigation track under `~/workspace/nba-player-track/reports/dob-investigation/`.
Sprint evidence read-only; nothing in the sprint's build directories was modified.
Investigation dates: 2026-10-15. Status: COMPLETE.

## Summary

The bridge sweep over 741 players produced exactly **3 DOB mismatches** (all
also listed in `curated/xwalk_quarantine.csv` with `failure_reason='dob-mismatch'`).
Independent verification (3+ sources each) resolved two of them and left one
genuinely ambiguous:

1. **Will Magnay** (espn 4278783, nba_id 1630266, bbref magnawi01, qid Q65658814):
   ESPN says 1998-07-10, NBA says 1998-06-10. Real DOB: **June 10, 1998**.
   **ESPN is wrong.** (9 confirming sources)
2. **Zach Edey** (espn 4600663, nba_id 1641744, bbref edeyza01, qid Q106817973):
   ESPN says 2002-03-14, NBA says 2002-05-14. Real DOB: **May 14, 2002**.
   **ESPN is wrong.** (10 confirming sources)
3. **Johnny Furphy** (espn 5157066, nba_id 1642277, bbref furphjo01, qid Q124624089):
   ESPN says 2004-12-07, NBA says 2004-12-08. Independent sources are split
   9 to 5. **Verdict: UNRESOLVED.** Correctly quarantined; excluded from the
   correction list.

The quarantine design worked as intended on all three: no side was picked at
discovery time, and the Furphy case proves why. A resolver that picked a side
would have emitted a correction that may itself be wrong.

## Complete mismatch set (verified against bytes)

### 1. Will Magnay — ESPN wrong

| Source | DOB | Agrees with |
|---|---|---|
| ESPN Core API `/athletes/4278783` | 1998-07-10T07:00Z | ESPN only |
| ESPN site.api common/v3 `displayDOB` | 10/7/1998 | ESPN only |
| ESPN website bio page (id 4278783) | 10/7/1998 | ESPN only |
| NBA stats API `commonplayerinfo` (1630266) | 1998-06-10T00:00:00 | real |
| Wikidata Q65658814 P569 | +1998-06-10 | real |
| Wikipedia | June 10, 1998 | real |
| Basketball-Reference | June 10, 1998 | real |
| RealGM | Jun 10, 1998 | real |
| Sportradar | 1998-06-10 | real |
| StatsCrew | June 10, 1998 | real |
| Sofascore | Jun 10, 1998 | real |

9-to-1 against ESPN. ESPN is the odd one out, consistently, across its own
surfaces and against every independent source.

### 2. Zach Edey — ESPN wrong

| Source | DOB | Agrees with |
|---|---|---|
| ESPN Core API `/athletes/4600663` | 2002-03-14T08:00Z | ESPN only |
| ESPN site.api common/v3 `displayDOB` | 14/3/2002 | ESPN only |
| ESPN Grizzlies roster payload | 2002-03-14T08:00Z | ESPN only |
| NBA stats API `commonplayerinfo` (1641744) | 2002-05-14T00:00:00 | real |
| Wikidata Q106817973 P569 | +2002-05-14 | real |
| Wikipedia | May 14, 2002 | real |
| Basketball-Reference | May 14, 2002 | real |
| Sportradar | 2002-05-14 | real |
| StatMuse | May 14, 2002 | real |
| TheSportsDB | May 14, 2002 | real |
| Simple Wikipedia | May 14, 2002 | real |
| sportsjone | 14 May 2002 | real |
| sportskeeda | May 14, 2002 | real |

10-to-1 against ESPN. Three separate ESPN surfaces (Core API, display API,
team roster) carry the identical wrong value, which pins the corruption to
ESPN's underlying athlete record, not to any one API's serialization.

Downstream echo: one bio aggregator's structured table repeats ESPN's wrong
"Mar 14, 2002" while its own prose says May 14. ESPN's bad value is already
propagating to scraper sites, which strengthens the fix-at-source case.

### 3. Johnny Furphy — UNRESOLVED (split sources)

| Source | DOB |
|---|---|
| ESPN Core API `/athletes/5157066` | 2004-12-07T08:00Z |
| Sportradar | 2004-12-07 |
| Wikidata Q124624089 P569 | +2004-12-07 |
| sportingnews (US and AU editions) | December 7, 2004 |
| thesportsgrail | December 7, 2004 |
| sportskeeda | 07-12-2004 |
| nbascoutinglive | 12/7/2004 |
| scoutbasketball | December 7, 2004 |
| NBA stats API `commonplayerinfo` (1642277) | 2004-12-08T00:00:00 |
| Wikipedia | 8 December 2004 (Melbourne) |
| Basketball-Reference FAQ | December 8, 2004 |
| StatMuse | Dec 8, 2004 |
| RealGM | Dec 8, 2004 |

Nine sources for December 7, five for December 8. Neither side meets the bar
for a confident "publisher is wrong" declaration, so no verdict is issued and
Furphy is excluded from the correction list. The one-day gap is consistent
with a UTC-vs-local-time artifact in the primary record (born in Melbourne,
UTC+10/+11: December 8 local is December 7 UTC), and Australian-originated
sources skew toward the 7th — but that remains a hypothesis, not a finding.

## Pattern analysis: one pattern or two?

The three cases fall into two distinct classes:

- **Class A — month-component errors, ESPN at fault, resolvable (Magnay, Edey).**
  Only the month differs; day and year are identical. But the deltas are NOT
  uniform: Magnay's ESPN value is +30 days (+1 month) vs real; Edey's is
  -61 days (-2 months) vs real. Opposite signs, different magnitudes.
- **Class B — day-level ambiguity (Furphy).** Off by one day, independent
  sources split; no fault assignable.

Does Furphy crack the month-shift theory open? The "month shift" was an
observation about two cases, never a mechanical theory, and the three cases
together retire the idea of a single uniform corruption mechanism. The
evidence kills every uniform-mechanism hypothesis on the record:

- Timezone shift: KILLED. Crossing a month boundary requires >24h; both
  Class A cases are mid-month with identical days.
- MM/DD vs DD/MM misparse: KILLED. Edey's day (14) exceeds 12; Magnay's
  swap would give October 6, not July 10.
- 0-indexed vs 1-indexed month: KILLED. Would shift June to May and May to
  April; observed June to July and May to March.
- Uniform day shift: KILLED. +30d, -61d, -1d are not constant.
- No documented community/GitHub report of ESPN Core API DOB corruption was
  found (three independent searches, 2026-10-15). Logged as a negative result.

**Surviving explanation (Class A):** per-record data-entry error (or an early
bad import never corrected) in ESPN's athlete store. The corruption is at the
record level — proven by cross-surface agreement within ESPN — but the
mechanism varies per record. Confidence: MODERATE (n=2 resolvable cases;
ESPN at fault in both; NBA agreed with independent sources in all 3).

**Observation (not a claim):** all three mismatched players are international
(Magnay AUS, Edey CAN, Furphy AUS). Whether international-born players are
overrepresented among mismatches is testable against the corpus baseline but
is not established here.

## Common-cause assessment (confidence levels)

| Claim | Confidence | Basis |
|---|---|---|
| Magnay: ESPN wrong, real DOB June 10, 1998 | HIGH | 9 independent sources; cross-surface consistency of wrong value |
| Edey: ESPN wrong, real DOB May 14, 2002 | HIGH | 10 independent sources; 3 ESPN surfaces carry the same wrong value |
| Furphy: genuinely ambiguous, no fault assignable | HIGH | 9-vs-5 source split; quarantined, not corrected |
| No single mechanical corruption mechanism (no uniform shift/parse bug) | MODERATE | Non-uniform deltas (+30d, -61d, -1d); 4 uniform hypotheses killed |
| Class A cause = per-record data-entry error in ESPN's athlete store | MODERATE | Record-level (cross-surface agreement); no uniform signature |
| Furphy = UTC-vs-local primary-record ambiguity | LOW | Consistent with geography and source split; unverified |
| International-player correlate | WEAK | 3/3 but no corpus baseline computed |

## Discovery methodology (generalized)

1. **Identity by ID keys only.** ESPN athlete ID, NBA stats person ID,
   basketball-reference slug, Wikidata QID. Never name-match for mechanics;
   names are labels.
2. **3-leg round trip.** (a) ESPN Core API `/athletes/{id}`: accept only HTTP
   200 with response id matching the request; capture `dateOfBirth`.
   (b) basketball-reference player page: accept only HTTP 200 (independence
   leg and third identity anchor). (c) NBA stats `commonplayerinfo`:
   capture `BIRTHDATE`.
3. **Date-part comparison.** Reduce both to YYYY-MM-DD and compare. Any
   disagreement quarantines with `failure_reason='dob-mismatch'`. Never
   resolve by picking a timezone side or a majority vote at discovery time.
   (Use the ISO `dateOfBirth`, never the locale-formatted `displayDOB`
   like "14/3/2002", which is ambiguous below the 13th.)
4. **Independent verification.** Pull every available DOB from sources with
   independent editorial provenance (Wikidata P569, Wikipedia,
   Basketball-Reference, RealGM, Sportradar, official team pages). Tabulate
   who-agrees-with-whom; the consistent odd one out is the at-fault
   publisher. Bar: 3+ agreeing sources before declaring a publisher wrong
   in a correction. Scrapers echoing a disputant's value do not count.
   A genuine source split (Furphy) means no verdict: the quarantine stands.
5. **Corruption classification.** Component analysis (which of Y/M/D differ),
   exact day-count deltas, and kill-criteria for each mechanism class
   (timezone <=24h, MM/DD day>12, zero-index uniform -1, uniform N-day).
   Cross-surface check within the at-fault publisher: if its site API,
   roster payloads, and website all carry the same value, the corruption is
   record-level, not serialization.
6. **Distinguishing systematic corruption from timezone noise.** Timezone
   artifacts produce <=1-day deltas near day boundaries and identical values
   across sources that share a record. Systematic corruption produces
   component-level changes (month/year) and survives cross-surface checks.
   Furphy sits exactly on the boundary: day-level AND source-split, which is
   why it gets no verdict.

## Correction list

| espn_id | nba_id | bbref | qid | Player | ESPN serves | Correct | Evidence |
|---|---|---|---|---|---|---|---|
| 4278783 | 1630266 | magnawi01 | Q65658814 | Will Magnay | 1998-07-10 | 1998-06-10 | Wikidata P569; Wikipedia; bbref; RealGM; Sportradar; StatsCrew; Sofascore; NBA stats API |
| 4600663 | 1641744 | edeyza01 | Q106817973 | Zach Edey | 2002-03-14 | 2002-05-14 | Wikidata P569; Wikipedia; bbref; Sportradar; StatMuse; TheSportsDB; Simple Wikipedia; sportsjone; sportskeeda; NBA stats API |

Excluded: Johnny Furphy (5157066) — source split, no verdict.

## Recommendations

1. **Send the correction email** (draft in `CORRECTION-EMAIL-DRAFT.md`) for the
   two resolved players.
2. **Correction-efficacy monitor:** re-run the 3-leg round trip for the two
   quarantined espn_ids after sending; record when ESPN's value flips. This
   closes the accountability loop the investigation was built for.
3. **Cross-surface consistency scan:** for all 741 athletes, fetch
   `site.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{id}`
   and compare `displayDOB` (D/M/YYYY) against the Core `dateOfBirth` ISO
   date-part already in `roundtrip_log.jsonl`. Any divergence reveals a
   serialization-layer corruption class this investigation did not see.
4. **International-share test:** compute international-born share among the
   741 vs among mismatches (birthPlace is in the ESPN leg payloads) to test
   the pipeline hypothesis.
5. **Keep the fail-closed rule.** The Furphy case is the proof that
   quarantine-first is load-bearing: majority vote would have been wrong in
   either direction.

## Addendum: surfacing more (2026-10-15 ~18:45 EDT)

Two additional discovery scans were run after the initial 3-case report.

### A. ESPN cross-surface roster scan (30 teams, 627 athletes with DOB)

Compared `dateOfBirth` from every NBA team roster payload
(`site.api.espn.com/.../teams/{id}/roster`) against the Core athlete
`dateOfBirth` in `roundtrip_log.jsonl`, and against NBA stats `BIRTHDATE`.

- Roster vs Core: **0 divergences in 627.** ESPN is perfectly self-consistent
  across surfaces at scale. This rules out a serialization-layer corruption
  class and confirms the Class A errors live in ESPN's athlete record.
- Roster vs NBA: **2 divergences**, exactly the known Edey and Furphy cases
  (Magnay is not on a current NBA roster). Nothing new.

### B. Wikidata third-leg triangulation (737 QIDs)

Compared Wikidata P569 against the ESPN/NBA consensus DOB for every player
where ESPN and NBA agreed. This catches the class the 2-publisher pipeline is
blind to: both publishers agreeing on the same wrong value.

- **Ky Bowman** (espn 4065635, nba_id 1629065, bbref bowmaky01, qid Q63119820):
  ESPN and NBA both say **June 16, 1997**. Wikidata carries a June 17 claim —
  but Wikidata itself holds BOTH values (+1997-06-17 and +1997-06-16), and
  every independent source (Wikipedia, Basketball-Reference, StatMuse, FIBA,
  Sofascore, Proballers, ESPN bio page) says June 16. The one June-17 echo
  outside Wikidata (bornglorious) derives from the Wikidata QID, so it is not
  independent. **Verdict: Wikidata is the outlier; ESPN/NBA consensus stands.**
  No ESPN correction needed. A Wikidata fix is Justin's call (public-KB edit).
- Cam Spencer (espn 4433083, qid Q100925863): apparent divergence was a
  Wikidata year-precision claim (+2000-00-00, precision 9) alongside a
  day-precision +2000-04-06 that agrees with ESPN/NBA. Not a real divergence.

### Remaining ways to surface more

1. **displayDOB-vs-ISO scan:** fetch `site.api/.../athletes/{id}` for all 741
   and compare locale `displayDOB` against Core ISO date-part. Would catch a
   display-serialization corruption class; ~741 requests.
2. **Corpus expansion:** the 3-leg methodology generalizes to any player set
   (all-time NBA, WNBA, G League). The international-player correlate (3/3 so
   far) suggests prioritizing international players if expanding.
3. **Re-run monitor:** re-trip the quarantined espn_ids after the correction
   email goes out; record when ESPN's values flip. Also catches future drift.
4. **Wikidata watch:** the Bowman case shows third-publisher triangulation is
   worth running on a schedule, not just once.

### C. Timezone-stratified scan (2026-10-15 ~19:08 EDT, subagent)

61 players across 17 UTC-offset buckets (3-5 per bucket), birthplaces resolved
via Wikidata for all 741 corpus QIDs, offsets assigned per birthplace standard
time. Tested whether DOB disagreements correlate with birthplace UTC offset.

- **Timezone mechanism KILLED as a general explanation (HIGH confidence).**
  A UTC-normalization mechanism predicts ESPN-earlier at positive offsets and
  ESPN-later at negative offsets. Observed: Magnay (UTC+10) ESPN *later* by
  30d; Edey (UTC-5) ESPN *earlier* by 61d — contradicted twice over. Month-level
  deltas cannot be timezone artifacts at all.
- Raw clustering at |offset|=10 (2/13 vs 1/728, Fisher p=0.0020) is real but
  post-hoc and confounded by Magnay's month-level case. Day-level-only test:
  p=0.027 on n=1 (Furphy alone) — cannot confirm or refute. Verdict on
  "day-level ambiguity arises from UTC-vs-local at large offsets": UNRESOLVED,
  LOW confidence, one consistent data point.
- No new mismatches surfaced in the stratified sample or zone-fill attempts
  (UTC-10, -9, +5:30, +6, +7, +11 probed; no resolvable outside-corpus players).
- The |10| bucket is the corpus's mismatch hotspot — priority bucket for the
  re-run monitor.
- Incidental: a fourth `dob_match` anomaly in the log (espn 2991139, Kris
  Dunn) is `dob_match: null` from an NBA-leg transport timeout
  (stats.nba.com ReadTimeout), not a DOB conflict. The 3-case count stands.

Full writeup: timezone-scan/FINDINGS.md in this directory.

### D. displayDOB-vs-ISO scan, all 741 athletes (2026-10-15 ~19:39 EDT)

Fetched `site.api/.../common/v3/sports/basketball/nba/athletes/{id}` for all
741 and compared locale `displayDOB` (D/M/YYYY) against the Core `dateOfBirth`
ISO date-part, counting a match if EITHER the D/M or M/D reading agreed (the
format is ambiguous below the 13th).

- **0 divergences in 741.** Three transient fetch errors retried clean, all
  matching. Saved: displaydob_scan.json.
- Combined with scan A (roster payloads, 0/627), this closes the
  serialization-layer question: no display-layer corruption class exists in
  this corpus. ESPN's surfaces are fully self-consistent; the Class A errors
  are record-level, full stop.

### E. WNBA scan (2026-10-15 ~19:44 EDT, subagent)

221 unique rostered athletes across 15 WNBA teams (incl. expansion Valkyries,
Portland Fire, Toronto Tempo). ESPN Core DOB live for 221/221. bbref WNBA
index scraped (1,217 slugs): 212 joined, 1 verified name-variant bridge, 8
coverage-gap players checked individually. The stats-API leg has no ID-keyed
bridge for WNBA (ESPN payloads carry no stats ID; Wikidata sports-ID coverage
~zero), so the scan ran as ESPN-vs-bbref/Wikidata+independents per the
authorized fallback.

**2 new mismatches, both ESPN wrong (HIGH confidence):**

| espn_id | qid | Player | ESPN serves | Correct | Class | Sources |
|---|---|---|---|---|---|---|
| 5017605 | Q106587773 | Kamila Borkowska | 2002-06-26 | 2002-07-26 | month-only (ESPN one month early) | Wikidata P569; Valencia Basket official announcement; RealGM; Sofascore; Flashscore; SportsGrid |
| 4433744 | Q119545957 | Ugonne "Michelle" Onyiah | 2003-03-12 | 2002-03-12 | year-only (ESPN one year late) — new class | Wikidata P569; Sportradar; FIBA; SportsGrid; Spotrac; Flashscore |

Note on Onyiah: Wikipedia alone says 2002-08-12 — a separate lone-outlier
error on Wikipedia's side, not the correction target.

213/213 ESPN-vs-bbref comparisons clean. 0 unresolved splits.

**Methodological finding:** ESPN athlete IDs are league-scoped, not global
(WNBA DeWanna Bonner = espn 869 = NBA Keith Van Horn). Any cross-league work
must key on the uid's league segment.

Full writeup: wnba-scan/WNBA-FINDINGS.md in this directory.
