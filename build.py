"""Build a static Stremio catalog addon: TMDB picks each row's titles,
IMDb's public ratings dataset sorts them. Output goes to docs/ (GitHub Pages).

Env: TMDB_TOKEN (TMDB v4 read access token). Optional ROWS=id1,id2 to build a subset.
Stdlib only.
"""
import csv, datetime, gzip, io, json, os, shutil, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

from rows import BLOCK, MIN_RATING, ROWS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
CACHE = os.path.join(ROOT, "cache", "imdb_ids.json")
TOKEN = os.environ["TMDB_TOKEN"]
PAGE = 100          # items per catalog file; Stremio asks for skip=100, 200, ...
MAX_ITEMS = 300     # per row / per genre
RPDB = "https://api.ratingposterdb.com/t0-free-rpdb-rounded-blocks/imdb/poster-default/{}.jpg?fallback=true"
TMDB_KIND = {"movie": "movie", "series": "tv"}


def get(url, headers=None, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def tmdb(path, **params):
    q = urllib.parse.urlencode(params)
    return json.loads(get(f"https://api.themoviedb.org/3/{path}?{q}", {"Authorization": f"Bearer {TOKEN}"}))


def imdb_ratings():
    raw = gzip.decompress(get("https://datasets.imdbws.com/title.ratings.tsv.gz")).decode()
    rows = csv.reader(io.StringIO(raw), delimiter="\t")
    next(rows)
    return {t: (float(r), int(v)) for t, r, v in rows}


def genre_names():
    names = {}
    for kind in ("movie", "tv"):
        for g in tmdb(f"genre/{kind}/list")["genres"]:
            names[g["id"]] = g["name"].replace(" & ", " and ")
    return names


def candidates(row):
    kind = TMDB_KIND[row["type"]]
    params = {"sort_by": "vote_count.desc", "include_adult": "false", **row["params"]}
    if row.get("recent_years"):
        since = datetime.date.today().replace(year=datetime.date.today().year - row["recent_years"])
        params["primary_release_date.gte" if kind == "movie" else "first_air_date.gte"] = since.isoformat()
    out = []
    for page in range(1, row["pages"] + 1):
        data = tmdb(f"discover/{kind}", page=page, **params)
        out += data["results"]
        if page >= data.get("total_pages", 0):
            break
    return out


def main():
    only = set(filter(None, os.environ.get("ROWS", "").split(",")))
    rows = [r for r in ROWS if not only or r["id"] in only]
    ratings = imdb_ratings()
    gnames = genre_names()
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

    built = {}
    for row in rows:
        cands = candidates(row)
        kind = TMDB_KIND[row["type"]]
        missing = [c["id"] for c in cands if f"{kind}:{c['id']}" not in cache]
        with ThreadPoolExecutor(8) as ex:
            for tid, ext in zip(missing, ex.map(lambda i: tmdb(f"{kind}/{i}/external_ids"), missing)):
                cache[f"{kind}:{tid}"] = ext.get("imdb_id") or ""
        items, seen = [], set()
        for c in cands:
            tt = cache.get(f"{kind}:{c['id']}")
            if not tt or tt in seen or tt in BLOCK or tt not in ratings:
                continue
            rating, votes = ratings[tt]
            if rating < MIN_RATING or votes < row["min_votes"]:
                continue
            seen.add(tt)
            date = c.get("release_date") or c.get("first_air_date") or ""
            items.append(dict(
                id=tt, type=row["type"], name=c.get("title") or c.get("name"),
                poster=RPDB.format(tt), posterShape="poster", releaseInfo=date[:4],
                imdbRating=f"{rating:.1f}", description=c.get("overview") or "",
                background=f"https://image.tmdb.org/t/p/w1280{c['backdrop_path']}" if c.get("backdrop_path") else None, genres=[gnames[g] for g in c.get("genre_ids", []) if g in gnames],
                _votes=votes,
            ))
        items.sort(key=lambda m: (-float(m["imdbRating"]), -m["_votes"]))
        built[row["id"]] = items
        print(f"{row['id']:16} candidates={len(cands):5} kept={len(items):4} top={[m['name'] for m in items[:3]]}")

    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, "w"), separators=(",", ":"), sort_keys=True)
    write(rows, built)


def write(rows, built):
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    catalogs = []
    for row in rows:
        items = built[row["id"]]
        genres = sorted({g for m in items for g in m["genres"]})
        if row.get("home"):
            extra = [dict(name="genre", options=genres), dict(name="skip")]
        else:  # required genre keeps the row off Home; "All" is the default
            genres = ["All"] + genres
            extra = [dict(name="genre", options=genres, isRequired=True), dict(name="skip")]
        catalogs.append(dict(type=row["type"], id=row["id"], name=row["name"], extra=extra))
        base = os.path.join(OUT, "catalog", row["type"], row["id"])
        variants = {None: items} if row.get("home") else {}
        for g in genres:
            variants[g] = items if g == "All" else [m for m in items if g in m["genres"]]
        for g, lst in variants.items():
            lst = lst[:MAX_ITEMS]
            for skip in range(0, max(len(lst), 1), PAGE):
                parts = ([f"genre={g}"] if g else []) + ([f"skip={skip}"] if skip else [])
                path = base + ".json" if not parts else os.path.join(base, "&".join(parts) + ".json")
                os.makedirs(os.path.dirname(path), exist_ok=True)
                metas = [{k: v for k, v in m.items() if k != "_votes" and v is not None} for m in lst[skip:skip + PAGE]]
                json.dump({"metas": metas}, open(path, "w"), separators=(",", ":"))
    manifest = dict(
        id="org.liamcanning.imdbrows", version="1.0." + datetime.date.today().strftime("%Y%m%d"),
        name="IMDb Rows", description="Curated rows sorted by IMDb rating, rebuilt weekly.",
        resources=["catalog"], types=["movie", "series"], idPrefixes=["tt"], catalogs=catalogs,
        behaviorHints=dict(configurable=False),
    )
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    open(os.path.join(OUT, ".nojekyll"), "w").close()


if __name__ == "__main__":
    sys.exit(main())
