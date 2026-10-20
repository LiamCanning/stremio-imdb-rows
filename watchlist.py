"""Liam's public IMDb watchlist as two catalogs (films, series), highest IMDb rating first.

IMDb blocks plain requests with an AWS WAF challenge, so the page is read
through Jina Reader. TMDB supplies type, name, year, overview and backdrop.
Writes catalog files to <out>/catalog/<type>/watchlist*.json, plus a "Foreign"
row (origin outside the US and UK, or not in English) with a country filter in
<out>/catalog/<type>/foreign*. Foreign titles are tagged with their country code,
e.g. "[ES] Money Heist", wherever meta() is used. The manifest entries live in build.py. If Jina can't deliver the full list (it sometimes
blocks anonymous access to imdb.com for hours), the live Pages copy is reused,
so a bad fetch never deploys an empty row or blocks the rest of the build.
Set JINA_API_KEY to read through Jina as a signed-in user. Stdlib only.

Usage: python watchlist.py <out_dir>
"""
import functools, json, os, re, sys, time
import urllib.error

from build import FOREIGN, PAGE, RPDB, get, imdb_ratings, tmdb

URL = "https://www.imdb.com/user/p.hzr7i7clzkng37xjalyrjrvfki/watchlist/?sort=date_added%2Cdesc"
LIVE = "https://liamcanning.github.io/stremio-imdb-rows/catalog/{}/{}.json"
HOME = {"US", "GB"}


def watchlist_ids():
    # Jina sometimes returns a half-loaded page; retry until the ids match the page's own count.
    # Signed-in reads don't always show that count, so two identical full reads in a row also pass.
    headers = {"x-no-cache": "true", "X-With-Links-Summary": "all"}
    if os.environ.get("JINA_API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["JINA_API_KEY"]
    prev = None
    for attempt in range(6):
        md = get("https://r.jina.ai/" + URL, headers).decode()
        found = {}
        for tt, pos in re.findall(r"imdb\.com/title/(tt\d+)/\?ref_=wl_t_(\d+)", md):
            found.setdefault(tt, int(pos))
        total = re.search(r"\n(\d+)\s*\n?\s*(?:items?|titles?)\s*\n", md)
        print(f"watchlist attempt {attempt + 1}: {len(found)} ids parsed, page says {total.group(1) if total else '?'}")
        if total and found and len(found) >= int(total.group(1)):
            return sorted(found, key=found.get)
        if not total and len(found) > 25 and len(found) == prev:
            return sorted(found, key=found.get)
        prev = len(found)
        time.sleep(15)
    raise RuntimeError("never got the full list")


def write_pages(base, lst, genre=None):
    for skip in range(0, max(len(lst), 1), PAGE):
        parts = ([f"genre={genre}"] if genre else []) + ([f"skip={skip}"] if skip else [])
        path = base + ".json" if not parts else os.path.join(base, "&".join(parts) + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump({"metas": lst[skip:skip + PAGE]}, open(path, "w"), separators=(",", ":"))


def keep_live(out):
    # copy the currently deployed watchlist pages so the rows stay as they were
    for kind in ("movie", "series"):
        for row, genre in [("watchlist", None), ("foreign", None)] + [("foreign", g) for g in FOREIGN]:
            base = os.path.join(out, "catalog", kind, row)
            os.makedirs(base, exist_ok=True)
            skip = 0
            while True:
                parts = ([f"genre={genre}"] if genre else []) + ([f"skip={skip}"] if skip else [])
                rel = row + ("/" + "&".join(parts) if parts else "")
                try:
                    data = get(LIVE.format(kind, rel.replace(" ", "%20")), tries=2)
                except urllib.error.HTTPError as e:
                    if e.code != 404:
                        raise
                    if not skip:  # row not deployed yet
                        write_pages(base, [], genre)
                    break
                open(os.path.join(out, "catalog", kind, rel + ".json"), "wb").write(data)
                skip += PAGE
        print(f"watchlist {kind}: kept live copy")


@functools.cache
def names(kind):
    # ISO code -> English name, for "configuration/countries" and "configuration/languages"
    key = "iso_3166_1" if kind == "countries" else "iso_639_1"
    return {x[key]: x["english_name"] for x in tmdb(f"configuration/{kind}")}


def origin(m, kind, c):
    # tag titles made outside the US/UK, or not in English: "[ES] Money Heist", country in the description
    lang = c.get("original_language") or ""
    if kind == "series":
        codes = c.get("origin_country") or []
    else:
        d = tmdb(f"movie/{c['id']}")
        codes = d.get("origin_country") or [x["iso_3166_1"] for x in d.get("production_countries", [])]
    abroad = [x for x in codes if x not in HOME]
    if lang == "en" and (not abroad or set(codes) & HOME):
        return
    country = names("countries").get(abroad[0], abroad[0]) if abroad else "Other"
    language = names("languages").get(lang, lang)
    m["name"] = f"[{abroad[0] if abroad else lang.upper()}] {m['name']}"
    m["country"] = country
    original = c.get("original_title") or c.get("original_name")
    note = ", ".join(x for x in (country if abroad else "", language) if x)
    if original and original != (c.get("title") or c.get("name")):
        note += f". Original title: {original}"
    m["description"] = f"{note}.\n\n{m['description']}".strip()
def meta(tt):
    res = tmdb(f"find/{tt}", external_source="imdb_id")
    # series first: TMDB wrongly attaches some series' IMDb ids to a film too (BoJack, The Agency)
    for kind, key, date_key in (("series", "tv_results", "first_air_date"), ("movie", "movie_results", "release_date")):
        if res.get(key):
            c = res[key][0]
            m = dict(id=tt, type=kind, name=c.get("title") or c.get("name"), poster=RPDB.format(tt),
                     posterShape="poster", releaseInfo=(c.get(date_key) or "")[:4], description=c.get("overview") or "")
            if c.get("backdrop_path"):
                m["background"] = f"https://image.tmdb.org/t/p/w1280{c['backdrop_path']}"
            origin(m, kind, c)
            return m
    return None


def main(out):
    try:
        ids = watchlist_ids()
    except Exception as e:
        print(f"::warning::watchlist fetch failed ({e}); keeping the live copy")
        return keep_live(out)
    ratings = imdb_ratings()
    items = [m for m in map(meta, ids) if m]
    for m in items:
        if m["id"] in ratings:
            m["imdbRating"] = f"{ratings[m['id']][0]:.1f}"
    # unrated (unreleased) titles go last, in the order they were added
    items.sort(key=lambda m: (-ratings.get(m["id"], (0, 0))[0], -ratings.get(m["id"], (0, 0))[1]))
    for kind in ("movie", "series"):
        lst = [m for m in items if m["type"] == kind]
        write_pages(os.path.join(out, "catalog", kind, "watchlist"), lst)
        foreign = [m for m in lst if "country" in m]
        base = os.path.join(out, "catalog", kind, "foreign")
        write_pages(base, foreign)
        for g in FOREIGN:
            write_pages(base, [m for m in foreign if (m["country"] if m["country"] in FOREIGN else "Other") == g], g)
        print(f"watchlist {kind}: {len(lst)}, foreign {len(foreign)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
