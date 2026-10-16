# DOB Mismatch Discovery Methodology

Draft section for the final report. Status: Phase 4 draft, 2026-10-15.

## 1. The 3-leg round trip

Every player is identified by three publisher keys: ESPN athlete ID (`espn_id`),
NBA stats person ID (`nba_id`), and basketball-reference slug (`bbref`). No leg
uses name matching; names appear only as human-readable labels.

Leg 1 — ESPN Core API: `GET https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/athletes/{espn_id}?lang=en`.
Accept only HTTP 200 with the response `id` matching the requested ID. Capture `dateOfBirth` (ISO 8601).

Leg 2 — basketball-reference: `GET https://www.basketball-reference.com/players/{x}/{bbref}.html`.
Accept only HTTP 200. Acts as a reachability/independence leg: bbref's page is an
independent editorial record used later for verification, and its URL scheme is a
third independent identity anchor.

Leg 3 — NBA stats API: `commonplayerinfo` for `nba_id`. Capture `BIRTHDATE`.

Comparison: reduce both DOB values to their YYYY-MM-DD date parts and compare.
Any disagreement quarantines the player with `failure_reason='dob-mismatch'`.
The comparison NEVER resolves the conflict by picking a side (no timezone-side
picking, no majority-vote shortcut at discovery time): disagreement is a data
event, not a tie to break.

## 2. The independent-verification standard

A mismatch is a claim that at least one publisher is wrong. Declaring WHICH
publisher is wrong requires evidence independent of the two disputants:

- Pull every available DOB for the player from independent sources: Wikidata
  (P569, by QID — itself ID-keyed), Wikipedia, Basketball-Reference FAQ,
  RealGM, Sportradar, official team pages, FIBA records.
- Tabulate who agrees with whom. The odd one out across many sources IS the
  publisher at fault.
- Minimum bar: 3 independent sources agreeing on the real DOB before declaring
  a publisher wrong in a correction report. (This investigation used 6+ for
  Magnay and 8 for Edey.)
- Scrapers that echo a disputant's value (observed: a bio aggregator's table
  row repeating ESPN's wrong date while its prose said the right one) do not
  count as independent sources. Independence means independent editorial
  provenance, not a fresh crawl of the same bad value.

## 3. Corruption-pattern analysis

Once the full mismatch set is collected, classify each by difference type:
- Component analysis: which of year/month/day differ? (Both confirmed cases
  here were month-only, day and year identical.)
- Offset analysis: exact day-count deltas between the disputants' dates.
- Difference taxonomy checks, each with a kill criterion:
  - Timezone shift: requires <=24h delta to survive; anything crossing a month
    boundary with identical days kills it.
  - MM/DD vs DD/MM misparse: day > 12 in either reading kills it.
  - 0-indexed vs 1-indexed month: uniform -1 month shift required.
  - Uniform day shift (off-by-N): constant N across cases required.
- Cross-surface check within the at-fault publisher: if the publisher's other
  surfaces (site API, website display layer) carry the same wrong value, the
  corruption is in the publisher's underlying record, not in one API's
  serialization. (Confirmed here: ESPN Core API and ESPN site.api common/v3
  agree on the wrong month.)
- Correlate the at-fault side with player attributes (nationality/birthplace,
  draft year, roster status) to test pipeline hypotheses.

## 4. Correction-list format

Each row: `espn_id`, `nba_id`, `bbref` slug, `qid`, player name (label), the
wrong value as served, the correct value, the 3+ verifying sources with URLs,
and which publisher is wrong. Suitable for direct send to the at-fault
publisher's data team.
