"""Liam's Stremio Library, unwatched titles only, as two catalogs (films, series),
highest IMDb rating first.

Reads the Library from the Stremio API with STREMIO_AUTH_KEY. "Watched" follows
Stremio's own rule: played to the end at least once, or marked as watched.
Without the key it writes empty rows, so the rest of the site still deploys.
Stdlib only.

Usage: python library.py <out_dir>
"""
import json, os, sys, urllib.request

from build import PAGE, RPDB, imdb_ratings
from watchlist import meta


def library_items(key):
    body = json.dumps({"authKey": key, "collection": "libraryItem", "ids": [], "all": True}).encode()
    req = urllib.request.Request("https://api.strem.io/api/datastoreGet", data=body,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["result"]


def main(out):
    key = os.environ.get("STREMIO_AUTH_KEY")
    items = []
    if key:
        ratings = imdb_ratings()
        for i in library_items(key):
            st = i.get("state") or {}
            if i.get("removed") or i.get("temp") or not i["_id"].startswith("tt"):
                continue
            if st.get("timesWatched") or st.get("flaggedWatched"):
                continue
            m = meta(i["_id"]) or dict(id=i["_id"], name=i.get("name"), posterShape="poster")
            m.update(type=i["type"], poster=RPDB.format(i["_id"]))
            if i["_id"] in ratings:
                m["imdbRating"] = f"{ratings[i['_id']][0]:.1f}"
            items.append(m)
        items.sort(key=lambda m: (-ratings.get(m["id"], (0, 0))[0], -ratings.get(m["id"], (0, 0))[1]))
    else:
        print("library: no STREMIO_AUTH_KEY, writing empty rows")
    for kind in ("movie", "series"):
        lst = [m for m in items if m["type"] == kind]
        base = os.path.join(out, "catalog", kind, "library")
        os.makedirs(base, exist_ok=True)
        for skip in range(0, max(len(lst), 1), PAGE):
            path = base + ".json" if not skip else os.path.join(base, f"skip={skip}.json")
            json.dump({"metas": lst[skip:skip + PAGE]}, open(path, "w"), separators=(",", ":"))
        print(f"library {kind}: {len(lst)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
