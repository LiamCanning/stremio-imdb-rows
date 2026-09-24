"""Per-episode IMDb ratings as a Stremio stream resource.

Writes one static file per rated episode to <out>/stream/series/tt...:S:E.json,
holding a single non-playable "stream" that shows the rating and links to the
episode's IMDb page. Too many files to commit, so the workflow deploys them
straight to Pages. Stdlib only.

Usage: python episodes.py <out_dir>
"""
import gzip, io, json, os, sys
from collections import defaultdict

from build import get

MIN_SHOW_VOTES = 5000


def votes_label(v):
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 1000:
        return f"{v / 1000:.1f}k" if v < 10_000 else f"{v // 1000}k"
    return str(v)


def lines(url):
    with gzip.open(io.BytesIO(get(url)), "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            yield line.rstrip("\n").split("\t")


def main(out):
    ratings = {t: (float(r), int(v)) for t, r, v in lines("https://datasets.imdbws.com/title.ratings.tsv.gz")}
    seasons = defaultdict(list)  # (show, season) -> [(episode, ep_tt, rating, votes)]
    for ep_tt, show, s, e in lines("https://datasets.imdbws.com/title.episode.tsv.gz"):
        if s == "\\N" or e == "\\N" or s == "0" or ep_tt not in ratings:
            continue
        if ratings.get(show, (0, 0))[1] < MIN_SHOW_VOTES:
            continue
        seasons[(show, int(s))].append((int(e), ep_tt, *ratings[ep_tt]))

    base = os.path.join(out, "stream", "series")
    os.makedirs(base, exist_ok=True)
    count = 0
    for (show, s), eps in seasons.items():
        avg = sum(r for _, _, r, _ in eps) / len(eps)
        ranked = sorted(eps, key=lambda x: (-x[2], -x[3]))
        rank = {ep_tt: i + 1 for i, (_, ep_tt, _, _) in enumerate(ranked)}
        for e, ep_tt, rating, votes in eps:
            text = (f"IMDb {rating:.1f} ({votes_label(votes)} votes)\n"
                    f"Season {s} average {avg:.1f} · #{rank[ep_tt]} of {len(eps)} in season")
            stream = dict(name=f"IMDb {rating:.1f}", title=text, description=text,
                          externalUrl=f"https://www.imdb.com/title/{ep_tt}/")
            with open(os.path.join(base, f"{show}:{s}:{e}.json"), "w") as f:
                json.dump({"streams": [stream]}, f, ensure_ascii=False, separators=(",", ":"))
            count += 1
    print(f"episodes: {count} files across {len({k[0] for k in seasons})} shows")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
