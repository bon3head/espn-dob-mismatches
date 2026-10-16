# WNBA Scan — Request Log

All requests from this VM on 2026-10-15 (~19:00–20:30 EDT). Contact UA:
`CipherXwalk/1.0 (wnba dob-scan research)`. Sprint build dirs untouched
(read-only).

## 1. Roster harvest (site.api ESPN)
- `GET .../wnba/teams` → 15 teams (incl. expansion Valkyries/Fire/Tempo).
- `GET .../wnba/teams/{id}/roster` × 15, 0.4s spacing → 221 unique athletes,
  all with `dateOfBirth`. Saved `wnba_roster.json`.

## 2. Stats-leg attempts (stats.nba.com via track venv nba_api)
1. `commonplayerinfo.CommonPlayerInfo` signature check → has `league_id_nullable`.
2. `commonallplayers` LeagueID=10 season=2025 → 1,226 WNBA PERSON_IDs. Saved
   `wnba_stats_person_ids.json`.
3. `commonplayerinfo(player_id=203025, league_id_nullable='10')` → BIRTHDATE
   returned. Endpoint works for WNBA.
4. ESPN Core WNBA athlete payload inspection (id 869): no stats.nba.com ID;
   `alternateIds.sdr` is Sportradar; uid `s:40~l:59~a:869` is league-scoped.
5. Wikidata SPARQL bridge (P3685→espn, P3647→stats, filtered against the
   1,226 WNBA person_ids): 0 usable bridges. The 6 P3685 hits were
   cross-league collisions (e.g. Q555127 = NBA Keith Van Horn, espn 869 =
   WNBA DeWanna Bonner's number). A female-filtered variant also returned 0.
   DeWanna Bonner's own entity (Q866093) carries no P3685/P3647/P2685 at all.
- Conclusion: stats endpoint reachable, ID bridge nonexistent. Scan proceeded
  as ESPN-vs-bbref/Wikidata per the authorized fallback. No leg invented.

## 3. Key finding en route: ESPN IDs are league-scoped
WNBA espn 869 (DeWanna Bonner) == NBA espn 869 (Keith Van Horn). Cross-league
joins on bare ESPN IDs are unsafe; the uid's `l:` segment is the league key.

## 4. ESPN Core DOB leg (sports.core.api.espn.com, league=wnba)
- 221 `GET /athletes/{id}?lang=en`, 0.5s spacing, HTTP 200 + id-match required.
- 220/221 first pass; id 2490553 (Brittney Griner) transient empty response,
  retried 3× clean → 221/221. Saved `wnba_core_dob.json`.

## 5. bbref leg (basketball-reference.com/wnba)
- Index: `/wnba/players/` + 26 letter pages, 1.0s spacing → 1,217 slugs
  (slugs end in `w`; active-player links wrap names in `<strong>`).
  Saved `bbref_wnba_slug_index.json`.
- Join: normalized-name match roster→index → 212 unique, 0 ambiguous,
  9 missing. Saved `wnba_bbref_join.json` (provenance per row).
- Page fetch: 212 pages, 4.0s spacing (spec politeness), DOB from
  `data-birth="YYYY-MM-DD"`. 212/212 extracted. Saved `wnba_bbref_dob.json`.
- Variant bridge: Anastasiia Olairi Kosu → bbref "Anastasiia Kosu"
  (kosuan01w); identity confirmed (Russian birthplace + matching DOB).

## 6. Comparison
- 213 ESPN-vs-bbref date-part comparisons → **0 mismatches**.
- 8 no-bbref players checked vs Wikidata P569 / independent sources:
  6 consistent, **2 mismatches** (Borkowska, Onyiah) → full 3+-source
  verification each. See WNBA-FINDINGS.md.

## 7. Self-corrections during the scan
- First bbref slug scrape missed `<strong>`-wrapped active players (873 vs
  1,217 slugs); re-scraped with fixed regex.
- Two Wikidata P569 reads sliced `time[:10]` before stripping the `+`
  prefix, truncating dates; caught on inspection, re-fetched correctly.
- `wnba_mismatches.json` initially had a transposed QID for Borkowska;
  corrected to Q106587773.
