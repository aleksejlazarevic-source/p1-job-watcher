#!/usr/bin/env python3
"""Print new Studentski Servis listings (JSON lines) not seen in previous runs.

First run seeds the state file and prints nothing unless --emit-first is given.
"""
import html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

BASE = "https://www.studentski-servis.com/studenti/prosta-dela"
STATE = Path(__file__).with_name("seen.json")
MAX_PAGES = 10


def fetch(page):
    q = urllib.parse.urlencode({"page": page, "isci": 1, "sort": 1})
    req = urllib.request.Request(f"{BASE}?{q}", headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def parse(page_html):
    jobs = []
    for m in re.finditer(r'<article class="job-item" data-jobid="(\d+)">(.*?)</article>', page_html, re.S):
        jid, body = m.groups()
        titles = [clean(t) for t in re.findall(r"<h5[^>]*>(.*?)</h5>", body, re.S)]
        loc = re.search(r"icon-location\"></use></svg>(.*?)</p>", body, re.S)
        desc = re.search(r'<p class="description[^>]*>(.*?)</p>', body, re.S)
        pay = re.search(r'class="job-payment">.*?<strong>(.*?)</strong>', body, re.S)
        jobs.append({
            "id": jid,
            "title": " / ".join(t for t in titles if t),
            "location": clean(loc.group(1)) if loc else "",
            "pay": clean(pay.group(1)) if pay else "",
            "description": clean(desc.group(1))[:600] if desc else "",
            "url": f"{BASE}#job-{jid}",
        })
    return jobs


def main():
    first_run = not STATE.exists()
    seen = set(json.loads(STATE.read_text())) if not first_run else set()
    new, page_ids = [], set()
    for page in range(1, MAX_PAGES + 1):
        jobs = parse(fetch(page))
        ids = {j["id"] for j in jobs}
        if not jobs or ids <= page_ids:  # past the last page: site repeats it
            break
        page_ids |= ids
        fresh = [j for j in jobs if j["id"] not in seen]
        new += fresh
        if not first_run and len(fresh) < len(jobs):  # reached already-seen territory
            break
        time.sleep(1)
    STATE.write_text(json.dumps(sorted(seen | page_ids | {j["id"] for j in new})))
    if first_run and "--emit-first" not in sys.argv:
        print(f"seeded {len(page_ids)} ids", file=sys.stderr)
        return
    for j in new:
        print(json.dumps(j, ensure_ascii=False))


main()
