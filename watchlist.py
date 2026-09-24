"""Liam's public IMDb watchlist as two catalogs (films, series), highest IMDb rating first.

IMDb blocks plain requests with an AWS WAF challenge, so the page is read
through Jina Reader. TMDB supplies type, name, year, overview and backdrop.
Writes catalog files to <out>/catalog/<type>/watchlist*.json; the manifest
entries live in build.py. Fails loudly if nothing parses, so a bad fetch
never deploys an empty row. Stdlib only.

Usage: python watchlist.py <out_dir>
"""
import json, os, re, sys, time

from build import PAGE, RPDB, get, imdb_ratings, tmdb

URL = "https://www.imdb.com/user/p.hzr7i7clzkng37xjalyrjrvfki/watchlist/?sort=date_added%2Cdesc"


def watchlist_ids():
    # Jina sometimes returns a half-loaded page; retry until the ids match the page's own count
    for attempt in range(6):
        md = get("https://r.jina.ai/" + URL, {"x-no-cache": "true", "X-With-Links-Summary": "all"}).decode()
        found = {}
        for tt, pos in re.findall(r"imdb\.com/title/(tt\d+)/\?ref_=wl_t_(\d+)", md):
            found.setdefault(tt, int(pos))
        total = re.search(r"\n(\d+)\nitems?\n", md)
        print(f"watchlist attempt {attempt + 1}: {len(found)} ids parsed, page says {total.group(1) if total else '?'}")
        if total and found and len(found) >= int(total.group(1)):
            return sorted(found, key=found.get)
        time.sleep(15)
    sys.exit("watchlist: never got the full list, not deploying")


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
            return m
    return None


def main(out):
    ratings = imdb_ratings()
    items = [m for m in map(meta, watchlist_ids()) if m]
    for m in items:
        if m["id"] in ratings:
            m["imdbRating"] = f"{ratings[m['id']][0]:.1f}"
    # unrated (unreleased) titles go last, in the order they were added
    items.sort(key=lambda m: (-ratings.get(m["id"], (0, 0))[0], -ratings.get(m["id"], (0, 0))[1]))
    for kind in ("movie", "series"):
        lst = [m for m in items if m["type"] == kind]
        base = os.path.join(out, "catalog", kind, "watchlist")
        os.makedirs(base, exist_ok=True)
        for skip in range(0, max(len(lst), 1), PAGE):
            path = base + ".json" if not skip else os.path.join(base, f"skip={skip}.json")
            json.dump({"metas": lst[skip:skip + PAGE]}, open(path, "w"), separators=(",", ":"))
        print(f"watchlist {kind}: {len(lst)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
