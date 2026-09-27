"""Liam's Stremio Library, unwatched titles only, as two catalogs (films, series),
highest IMDb rating first. Also strips watched titles from every other row.

Reads the Library from the Stremio API with STREMIO_AUTH_KEY. "Watched" follows
Stremio's own rule: played to the end at least once, or marked as watched.
Without the key it writes empty rows, so the rest of the site still deploys.
Stdlib only.

Usage: python library.py <out_dir>
"""
import glob, json, os, re, sys, urllib.request

from build import PAGE, RPDB, imdb_ratings
from watchlist import meta


def library_items(key):
    body = json.dumps({"authKey": key, "collection": "libraryItem", "ids": [], "all": True}).encode()
    req = urllib.request.Request("https://api.strem.io/api/datastoreGet", data=body,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["result"]


def watched(i):
    st = i.get("state") or {}
    return bool(st.get("timesWatched") or st.get("flaggedWatched"))


def hide_watched(out, seen):
    # regroup each row's (and genre's) pages, drop watched titles, repage so every page stays full
    groups = {}
    for path in glob.glob(os.path.join(out, "catalog", "*", "**", "*.json"), recursive=True):
        rel = os.path.relpath(path, os.path.join(out, "catalog"))
        m = re.fullmatch(r"(.+?)(?:/(genre=[^&]+?))?(?:[/&]skip=(\d+))?\.json", rel)
        groups.setdefault((m.group(1), m.group(2)), []).append((int(m.group(3) or 0), path))
    dropped = 0
    for (base, genre), pages in groups.items():
        pages.sort()
        metas = [x for _, p in pages for x in json.load(open(p))["metas"]]
        keep = [x for x in metas if x["id"] not in seen]
        if len(keep) == len(metas):
            continue
        dropped += len(metas) - len(keep)
        for _, p in pages:
            os.remove(p)
        root = os.path.join(out, "catalog", base)
        for skip in range(0, max(len(keep), 1), PAGE):
            parts = ([genre] if genre else []) + ([f"skip={skip}"] if skip else [])
            path = root + ".json" if not parts else os.path.join(root, "&".join(parts) + ".json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json.dump({"metas": keep[skip:skip + PAGE]}, open(path, "w"), separators=(",", ":"))
    print(f"hid {dropped} watched entries across rows")


def main(out):
    key = os.environ.get("STREMIO_AUTH_KEY")
    items = []
    if key:
        ratings = imdb_ratings()
        lib = library_items(key)
        for i in lib:
            if i.get("removed") or i.get("temp") or not i["_id"].startswith("tt") or watched(i):
                continue
            m = meta(i["_id"]) or dict(id=i["_id"], name=i.get("name"), posterShape="poster")
            m.update(type=i["type"], poster=RPDB.format(i["_id"]))
            if i["_id"] in ratings:
                m["imdbRating"] = f"{ratings[i['_id']][0]:.1f}"
            items.append(m)
        items.sort(key=lambda m: (-ratings.get(m["id"], (0, 0))[0], -ratings.get(m["id"], (0, 0))[1]))
        # removed and Continue Watching items still count: watched is watched
        hide_watched(out, {i["_id"] for i in lib if watched(i)})
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
