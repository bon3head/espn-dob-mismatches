#!/usr/bin/env python3
import csv, json, sqlite3, subprocess, time, os

BASE = '/home/hatch/workspace/nba-player-track'
HERE = os.path.join(BASE, 'reports/dob-investigation')
DATA = os.path.join(HERE, 'data')
os.makedirs(DATA, exist_ok=True)

players, claims, seen = {}, [], set()

def add_player(key, **kw):
    p = players.setdefault(key, {'player_key': key, 'name': '', 'league': '',
                                 'espn_id': '', 'nba_id': '', 'bbref_slug': '', 'qid': ''})
    for k, v in kw.items():
        if v:
            p[k] = v

def add_claim(key, source, dob, retrieved_at='', note=''):
    if (key, source) in seen or not dob:
        return
    seen.add((key, source))
    claims.append((key, source, dob, retrieved_at, note))

rows = [json.loads(l) for l in open(f'{BASE}/curated/build-2026-10-15/roundtrip_log.jsonl')]
for r in rows:
    eid = str(r['espn'])
    key = f'espn-{eid}'
    add_player(key, league='NBA', espn_id=eid,
               nba_id=str(r.get('nba_id') or ''), bbref_slug=r.get('bbref') or '',
               qid=r.get('qid') or '')
    e, n, ts = r.get('espn_leg', {}), r.get('nba_leg', {}), r.get('ts', '')
    if e.get('outcome') == 'ok' and e.get('dob'):
        add_claim(key, 'espn-core', e['dob'][:10], ts)
    if n.get('outcome') == 'ok' and n.get('birthdate'):
        add_claim(key, 'nba-stats', n['birthdate'][:10], ts)

p569 = json.load(open(f'{HERE}/wikidata_third_leg.json'))['p569']
qid_to_key = {p['qid']: p['player_key'] for p in players.values() if p['qid']}
for q, raw in p569.items():
    if q in qid_to_key:
        add_claim(qid_to_key[q], 'wikidata-p569', raw.lstrip('+')[:10], '2026-10-15')

qids = sorted(qid_to_key)
for i in range(0, len(qids), 50):
    url = ('https://www.wikidata.org/w/api.php?action=wbgetentities&ids=' + '|'.join(qids[i:i+50])
           + '&props=labels&languages=en&format=json')
    out = subprocess.run(['curl', '-s', '--max-time', '40', url],
                         capture_output=True, text=True).stdout
    try:
        ents = json.loads(out)['entities']
    except Exception:
        continue
    for q, ent in ents.items():
        lab = ent.get('labels', {}).get('en', {}).get('value')
        if lab:
            players[qid_to_key[q]]['name'] = lab
    time.sleep(0.25)

wcore = json.load(open(f'{HERE}/wnba-scan/wnba_core_dob.json'))['core']
wbbref = json.load(open(f'{HERE}/wnba-scan/wnba_bbref_dob.json'))
wjoin = json.load(open(f'{HERE}/wnba-scan/wnba_bbref_join.json'))['matched']
for eid, rec in wcore.items():
    key = f'espn-{eid}'
    add_player(key, league='WNBA', espn_id=eid, name=rec.get('name', ''))
    if rec.get('dob'):
        add_claim(key, 'espn-core', rec['dob'][:10], rec.get('ts', ''))
    slug = (wjoin.get(eid) or {}).get('slug', '')
    if slug:
        players[key]['bbref_slug'] = slug
for eid, rec in wbbref.items():
    key = f'espn-{eid}'
    if key in players and rec.get('bbref_dob'):
        add_claim(key, 'basketball-reference', rec['bbref_dob'], rec.get('ts', ''))
players['espn-5017605']['qid'] = 'Q106587773'
players['espn-4433744']['qid'] = 'Q119545957'

MANUAL = {
 'espn-4278783': [
  ('espn-display','1998-07-10'),('wikipedia','1998-06-10'),('basketball-reference','1998-06-10'),
  ('realgm','1998-06-10'),('sportradar','1998-06-10'),('statscrew','1998-06-10'),('sofascore','1998-06-10')],
 'espn-4600663': [
  ('espn-display','2002-03-14'),('espn-roster','2002-03-14'),('wikipedia','2002-05-14'),
  ('basketball-reference','2002-05-14'),('sportradar','2002-05-14'),('statmuse','2002-05-14'),
  ('thesportsdb','2002-05-14'),('simple-wikipedia','2002-05-14'),('sportsjone','2002-05-14'),
  ('sportskeeda','2002-05-14')],
 'espn-5157066': [
  ('wikipedia','2004-12-08'),('basketball-reference','2004-12-08'),('statmuse','2004-12-08'),
  ('realgm','2004-12-08'),('sportradar','2004-12-07'),('sportingnews','2004-12-07'),
  ('thesportsgrail','2004-12-07'),('sportskeeda','2004-12-07'),('nbascoutinglive','2004-12-07'),
  ('scoutbasketball','2004-12-07')],
 'espn-4065635': [
  ('wikipedia','1997-06-16'),('basketball-reference','1997-06-16'),('statmuse','1997-06-16'),
  ('fiba','1997-06-16'),('sofascore','1997-06-16'),('proballers','1997-06-16'),('espn-bio','1997-06-16')],
 'espn-5017605': [
  ('wikidata-p569','2002-07-26'),('valencia-basket','2002-07-26'),('realgm','2002-07-26'),
  ('sofascore','2002-07-26'),('flashscore','2002-07-26'),('sportsgrid','2002-07-26')],
 'espn-4433744': [
  ('wikidata-p569','2002-03-12'),('sportradar','2002-03-12'),('fiba','2002-03-12'),
  ('sportsgrid','2002-03-12'),('spotrac','2002-03-12'),('flashscore','2002-03-12'),
  ('wikipedia','2002-08-12','lone outlier, not the correction target')],
}
for key, lst in MANUAL.items():
    for item in lst:
        add_claim(key, item[0], item[1], '2026-10-15', item[2] if len(item) > 2 else '')

verdicts = [
 ('espn-4278783','1998-07-10','1998-06-10','nba-stats','month-only','espn-wrong','1998-06-10','HIGH','Will Magnay; 9 independent sources vs ESPN'),
 ('espn-4600663','2002-03-14','2002-05-14','nba-stats','month-only','espn-wrong','2002-05-14','HIGH','Zach Edey; 10 independent sources vs ESPN; 3 ESPN surfaces agree on wrong value'),
 ('espn-5157066','2004-12-07','2004-12-08','nba-stats','day-only','unresolved','','HIGH','Johnny Furphy; independent sources split 9-5; no verdict issued'),
 ('espn-4065635','1997-06-16','1997-06-17','wikidata-p569','day-only','third-party-wrong','1997-06-16','HIGH','Ky Bowman; Wikidata is the outlier; 8 independent sources back Jun 16'),
 ('espn-5017605','2002-06-26','2002-07-26','wikidata-p569+independents','month-only','espn-wrong','2002-07-26','HIGH','Kamila Borkowska (WNBA); 6 independent sources vs ESPN'),
 ('espn-4433744','2003-03-12','2002-03-12','wikidata-p569+independents','year-only','espn-wrong','2002-03-12','HIGH','Michelle Onyiah (WNBA); 6 independent sources vs ESPN; Wikipedia lone outlier (Aug 12) not corrected'),
]

scans = [
 ('nba-bridge-2026-10-15','NBA 3-leg bridge sweep','2026-10-15',741,3,'ESPN Core vs NBA stats vs bbref, date-part comparison, fail-closed quarantine'),
 ('nba-roster-surface-2026-10-15','ESPN roster cross-surface scan','2026-10-15',627,0,'roster dateOfBirth vs Core dateOfBirth; 0 divergences'),
 ('nba-wikidata-thirdleg-2026-10-15','Wikidata P569 third-leg triangulation','2026-10-15',737,1,'P569 vs ESPN/NBA consensus; 1 third-party outlier (Bowman)'),
 ('nba-displaydob-2026-10-15','displayDOB vs ISO scan','2026-10-15',741,0,'locale displayDOB vs Core ISO date-part, ambiguity-aware; 0 divergences'),
 ('nba-timezone-2026-10-15','Timezone-stratified scan','2026-10-15',61,0,'3-5 players x 17 UTC buckets; TZ mechanism killed generally'),
 ('wnba-scan-2026-10-15','WNBA DOB scan','2026-10-15',221,2,'ESPN vs bbref/Wikidata+independents (no stats-ID bridge); 2 ESPN-wrong'),
]

schema = open(os.path.join(DATA, 'schema.sql')).read()

def write_csv(path, header, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

write_csv(f'{DATA}/players.csv',
          ['player_key','name','league','espn_id','nba_id','bbref_slug','qid'],
          [[p['player_key'],p['name'],p['league'],p['espn_id'],p['nba_id'],p['bbref_slug'],p['qid']]
           for p in sorted(players.values(), key=lambda x: x['player_key'])])
write_csv(f'{DATA}/dob_claims.csv',
          ['player_key','source','dob','retrieved_at','note'],
          [[c[0],c[1],c[2],c[3],c[4]] for c in claims])
write_csv(f'{DATA}/mismatch_verdicts.csv',
          ['player_key','espn_dob','disputant_dob','disputant','difference_class','verdict','correct_dob','confidence','notes'],
          verdicts)
write_csv(f'{DATA}/scans.csv',
          ['scan_id','name','ran_at','players_scanned','mismatches_found','method'],
          scans)

dbp = os.path.join(DATA, 'dob_mismatches.db')
if os.path.exists(dbp):
    os.remove(dbp)
con = sqlite3.connect(dbp)
con.executescript(schema)
for t, fn in [('players','players.csv'),('dob_claims','dob_claims.csv'),
              ('mismatch_verdicts','mismatch_verdicts.csv'),('scans','scans.csv')]:
    with open(os.path.join(DATA, fn)) as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames
        con.executemany(f"INSERT INTO {t} ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                        [tuple(r[c] for c in cols) for r in rdr])
con.commit()

print('players:', con.execute('SELECT COUNT(*) FROM players').fetchone()[0])
print('claims:', con.execute('SELECT COUNT(*) FROM dob_claims').fetchone()[0])
print('verdicts:', con.execute('SELECT COUNT(*) FROM mismatch_verdicts').fetchone()[0])
print('--- Magnay who-agrees-with-whom ---')
for r in con.execute("SELECT source, dob FROM dob_claims WHERE player_key='espn-4278783' ORDER BY dob, source"):
    print(r)
print('--- verdicts ---')
for r in con.execute('SELECT player_key, verdict, correct_dob, confidence FROM mismatch_verdicts'):
    print(r)
print('--- leagues ---')
for r in con.execute('SELECT league, COUNT(*) FROM players GROUP BY league'):
    print(r)
con.close()
print('OK')
