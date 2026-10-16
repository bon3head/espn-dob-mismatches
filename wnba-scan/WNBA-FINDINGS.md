# WNBA DOB-Mismatch Scan — Findings

Extension of the NBA DOB-mismatch investigation. Work under
`~/workspace/nba-player-track/reports/dob-investigation/wnba-scan/`.
Scan date: 2026-10-15. Status: COMPLETE.

## Coverage

- 15 WNBA teams (incl. 2026 expansion: Golden State Valkyries, Portland Fire, Toronto Tempo).
- 221 unique rostered athletes; ESPN Core DOB live for 221/221 (one transient
  failure on Brittney Griner retried clean).
- bbref WNBA slug index scraped (1,217 all-time slugs); 212/221 joined by
  normalized name (provenance: `name-join-bbref-index`), 1 more via verified
  name variant (Anastasiia Olairi Kosu = bbref "Anastasiia Kosu", kosuan01w;
  identity confirmed by matching DOB + Russian birthplace).
- 8 players with no bbref page (developmental / pre-debut / coverage lag):
  checked individually against Wikidata P569 and independent sources.

## Mismatches found: 2 (both ESPN wrong)

### 1. Kamila Borkowska (espn 5017605, qid Q106587773) — ESPN wrong, HIGH confidence

Month-only error, same class as NBA Magnay/Edey. ESPN is one month early.

| Source | DOB | Agrees with |
|---|---|---|
| ESPN Core API `/athletes/5017605` | 2002-06-26T07:00Z | ESPN only |
| ESPN roster payload | 2002-06-26 | ESPN only |
| ESPN site.api `displayDOB` | 26/6/2002 | ESPN only |
| Wikidata Q106587773 P569 | 2002-07-26 | real |
| Valencia Basket (official club announcement) | July 26, 2002 | real |
| RealGM | Jul 26, 2002 | real |
| Sofascore | Jul 26, 2002 | real |
| Flashscore | 26.07.2002 | real |
| SportsGrid | 07/26/2002 | real |

Real DOB: **July 26, 2002**. 6 independent sources vs ESPN's 3 self-consistent
surfaces (record-level corruption, not serialization).

### 2. Ugonne "Michelle" Onyiah (espn 4433744, qid Q119545957) — ESPN wrong, HIGH confidence

Year-component error (new class vs the NBA set): ESPN says 2003, six sources say 2002.

| Source | DOB | Agrees with |
|---|---|---|
| ESPN Core API `/athletes/4433744` | 2003-03-12 | ESPN only |
| ESPN site bio page (id 4433744) | 12/3/2003 | ESPN only |
| Wikidata Q119545957 P569 | 2002-03-12 | real |
| Sportradar | 2002-03-12 | real |
| FIBA (official player profile) | Mar 12, 2002 | real |
| SportsGrid | 03/12/2002 | real |
| Spotrac | Mar 12, 2002 | real |
| Flashscore | 12.03.2002 | real |
| Wikipedia | August 12, 2002 | neither (lone outlier) |

Real DOB: **March 12, 2002**. Note: Wikipedia alone says August 12, 2002 —
a separate lone-outlier error on Wikipedia's side, not ESPN's. (Caution: do
not "correct" ESPN toward Wikipedia's August date; the 6-source consensus is
March.)

## Clean results

- 213/213 ESPN-vs-bbref comparisons: **0 mismatches.** Spot-checked 5 random
  players (Maley, Plum, Held, Salaun, Gray) — genuine independent agreement.
- 6 of 8 coverage-gap players verified consistent ESPN-vs-independent:
  Matilde Villa (WD ✓), Elena Buenavida (WD ✓), Elizabeth Balogun (WD ✓),
  Maria Gakdeng (Sportradar/FIBA/Wikipedia/RealGM ✓), Deja Kelly
  (Sportradar/Wikipedia/RealGM ✓), Nia Brodie = Nia Coffey (Wikipedia/SportsGrid ✓).

## Correction list (append to main report)

| espn_id | qid | Player | ESPN serves | Correct | Evidence |
|---|---|---|---|---|---|
| 5017605 | Q106587773 | Kamila Borkowska | 2002-06-26 | 2002-07-26 | Wikidata P569; Valencia Basket official; RealGM; Sofascore; Flashscore; SportsGrid |
| 4433744 | Q119545957 | Ugonne "Michelle" Onyiah | 2003-03-12 | 2002-03-12 | Wikidata P569; Sportradar; FIBA; SportsGrid; Spotrac; Flashscore |

## Methodology notes (WNBA adaptations)

- **ESPN athlete IDs are league-scoped, not global.** WNBA DeWanna Bonner
  (espn 869) collides with NBA Keith Van Horn (espn 869, Q555127). Any
  cross-league work must disambiguate by league (uid `s:40~l:59~a:869`
  carries the league segment).
- **Stats leg: endpoint works, bridge doesn't.** stats.nba.com
  `commonplayerinfo` with `league_id_nullable='10'` returns WNBA BIRTHDATEs
  (verified), and `commonallplayers` LeagueID=10 lists 1,226 WNBA person_ids.
  But no ID-keyed ESPN↔stats bridge exists: ESPN payloads carry no stats ID
  (`alternateIds.sdr` is Sportradar), and Wikidata P3685/P3647 coverage for
  current WNBA roster players is ~zero. Five honest attempts logged in
  SCAN-LOG.md; scan ran as ESPN-vs-bbref/Wikidata per the fallback.
- **bbref WNBA slugs end in `w`** (e.g. `bonnede01w`) and active-player index
  links wrap names in `<strong>`; page DOB is machine-readable via
  `data-birth="YYYY-MM-DD"`.
- Bridge provenance is per-row: 212 `name-join-bbref-index`, 1
  `name-variant-verified`, 8 individual checks. No keyed bridge existed;
  the 3+-source verification step is the backstop against bad bridges.
