#!/usr/bin/env python3
"""Print new MojeDelo.com student-work ads (JSON lines) not seen in previous runs.

Feed: sitemap lists every live ad with its ID; only unseen IDs get a detail
fetch, and only ads typed "Študentsko delo" are printed. First run seeds the
state file (no output) unless --emit-first is given.
"""
import html, json, re, sys, time, urllib.request
from pathlib import Path

SITE = "https://www.mojedelo.com"
API = "https://api.mojedelo.com"
STATE = Path(__file__).with_name("seen_mojedelo.json")
STUDENT = "Študentsko delo"


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def api_headers():
    g = get(f"{API}/uploaded-files/config/www.mojedelo.com/jb.globals.js")
    pick = lambda k: re.search(rf'"{k}":"([^"]+)"', g).group(1)
    return {"tenantId": pick("tenantId"), "channelId": pick("jbChannelId"), "languageId": pick("defaultLanguageId")}


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def to_job(d, slug_url):
    loc = d.get("jobLocationInput") or (d.get("town") or {}).get("name") or ""
    regions = ", ".join(r["translation"] for r in d.get("regions") or [])
    modes = ", ".join(m["translation"] for m in d.get("workModes") or [])
    return {
        "id": d["id"],
        "title": d["title"],
        "location": " | ".join(x for x in (loc, regions, modes) if x),
        "pay": json.dumps(d["salary"], ensure_ascii=False) if d.get("salary") else "",
        "hours": (d.get("workTime") or {}).get("translation", ""),
        "company": (d.get("company") or {}).get("name", ""),
        "description": clean(d.get("jobDescription"))[:600],
        "url": slug_url,
        "source": "mojedelo",
    }


def main():
    first_run = not STATE.exists()
    seen = set(json.loads(STATE.read_text())) if not first_run else set()
    sm = get(f"{SITE}/sitemap-0.xml")
    ads = dict((i, u) for u, i in re.findall(r"<loc>(https://www\.mojedelo\.com/oglas/[^/<]+/([0-9a-f-]{36}))</loc>", sm))
    new_ids = [i for i in ads if i not in seen]
    found = []
    if not first_run or "--emit-first" in sys.argv:
        hdr = api_headers() if new_ids else {}
        for i in new_ids:
            try:
                d = json.loads(get(f"{API}/job-ads/{i}", hdr))["data"]
            except Exception as e:
                print(f"skip {i}: {e}", file=sys.stderr)
                continue
            if any(t["translation"] == STUDENT for t in d.get("employmentTypes") or []):
                found.append(to_job(d, ads[i]))
            time.sleep(0.3)
    STATE.write_text(json.dumps(sorted(seen | set(ads))))
    if first_run and "--emit-first" not in sys.argv:
        print(f"seeded {len(ads)} ids", file=sys.stderr)
        return
    for j in found:
        print(json.dumps(j, ensure_ascii=False))


main()
