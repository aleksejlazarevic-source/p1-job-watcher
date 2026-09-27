# Job Watcher — public sample

Two small scripts that watch Slovenian student-job listing sites and print
only the *new* postings since the last run. This is the scraping/dedup
building block from a larger personal job-search pipeline; the AI-based
criteria matching and notifications are private and not included here.

## Slovensko

### Kaj počne
`jobwatcher.py` prebira oglase za študentsko delo na strani
[Studentski servis](https://www.studentski-servis.com/studenti/prosta-dela).
`jobwatcher_mojedelo.py` prebira oglase, označene kot "Študentsko delo", na
strani [MojeDelo](https://www.mojedelo.com). Vsak zagon izpiše samo tiste
oglase, ki jih pri prejšnjem zagonu še ni bilo — vsak oglas kot ena vrstica
JSON.

### Kako deluje
- Vsak skript v svoji datoteki stanja (`seen.json`, `seen_mojedelo.json`)
  hrani ID-je že videnih oglasov; ti datoteki `.gitignore` izključuje iz
  repozitorija.
- Prvi zagon samo "poseje" stanje (zabeleži, kateri oglasi trenutno
  obstajajo) in ne izpiše ničesar, razen če ga zaženeš z zastavico
  `--emit-first`.
- Vsak naslednji zagon primerja trenutne oglase s shranjenim stanjem in
  izpiše samo nove.
- `jobwatcher.py` bere HTML strani neposredno, s pomočjo regularnih
  izrazov. `jobwatcher_mojedelo.py` najprej prebere celoten seznam oglasov
  iz datoteke sitemap.xml, nato za vsak nov ID povpraša API strani in
  obdrži samo oglase, označene kot "Študentsko delo".
- Oba skripta upočasnjujeta svoje zahteve (`time.sleep`) in uporabljata
  izključno standardno knjižnico Pythona — brez zunanjih odvisnosti.

### Kaj manjka
- Korak, ki nove oglase primerja z datoteko `criteria.example.md` (ali
  pravo `criteria.md`) in odloči, kateri so vredni obvestila, je del
  zasebnega cevovoda in tukaj ni vključen. `criteria.example.md` prikazuje
  samo obliko vhodne datoteke, ki jo ta korak bere.
- Ni razporejevalnika (pri meni teče kot uporabniška systemd storitev) —
  tukaj je treba skripta pognati ročno ali si razporejanje urediti sam.
- Ni avtomatiziranih testov.
- Oba skripta sta odvisna od trenutne oblike HTML-ja/API-ja teh dveh
  strani; če se stran spremeni, ju bo treba popraviti.

### Primer izpisa
Ker oba skripta bereta žive strani, resničnega zagona ni mogoče shraniti
kot ponovljiv primer. `sample_output_studentski.jsonl` in
`sample_output_mojedelo.jsonl` zato vsebujeta izmišljene vnose v natanko
taki obliki, kot bi jo skripta dejansko izpisala (glej spodaj angleški
opis polj).

### Poganjanje
Potreben je samo Python 3, brez dodatnih paketov.

```
python3 jobwatcher.py            # prvi zagon: poseje stanje, brez izpisa
python3 jobwatcher.py            # drugi zagon: izpiše nove oglase kot vrstice JSON

python3 jobwatcher_mojedelo.py
python3 jobwatcher_mojedelo.py
```

---

## English

### What it does
`jobwatcher.py` reads student-job listings from
[Studentski servis](https://www.studentski-servis.com/studenti/prosta-dela).
`jobwatcher_mojedelo.py` reads ads tagged "Študentsko delo" (student work)
from [MojeDelo](https://www.mojedelo.com). Each run prints only the postings
that weren't there on the previous run — one JSON object per line.

### How it works
- Each script keeps its own state file of already-seen ad IDs
  (`seen.json`, `seen_mojedelo.json`), which `.gitignore` keeps out of the repo.
- The first run only seeds that state (records what's currently live) and
  prints nothing unless run with `--emit-first`.
- Every later run compares the current listings against the state file and
  prints only the new ones.
- `jobwatcher.py` parses the page HTML directly with regular expressions.
  `jobwatcher_mojedelo.py` first reads the full ad list from the site's
  sitemap, then queries the site's API per new ID and keeps only ads typed
  "Študentsko delo".
- Both throttle their requests (`time.sleep`) and use only the Python
  standard library — no external dependencies.

### What's missing
- The step that matches new postings against `criteria.example.md` (or a
  real `criteria.md`) and decides which ones are worth a notification is
  part of a private pipeline and isn't included here. `criteria.example.md`
  only shows the shape of the input file that layer reads.
- No scheduler (mine runs as a user systemd service) — here the scripts have
  to be run by hand, or scheduled yourself.
- No automated tests.
- Both scripts depend on the current HTML/API shape of these two sites; if a
  site changes, the scripts will need updating.

### Example output
Because both scripts hit live sites, a real run can't be captured as a
reproducible example. `sample_output_studentski.jsonl` and
`sample_output_mojedelo.jsonl` hold made-up entries in exactly the shape a
real run would print:

- Studentski servis fields: `id`, `title`, `location`, `pay`, `description`, `url`.
- MojeDelo fields: the same, plus `hours`, `company`, and `source`.

### Running it
Needs only Python 3, no extra packages.

```
python3 jobwatcher.py            # first run: seeds state, prints nothing
python3 jobwatcher.py            # second run: prints new listings as JSON lines

python3 jobwatcher_mojedelo.py
python3 jobwatcher_mojedelo.py
```
