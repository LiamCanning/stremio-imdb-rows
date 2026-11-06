# IMDb Rows (Stremio addon)

Static Stremio catalog addon served from GitHub Pages. Install: `https://liamcanning.github.io/stremio-imdb-rows/manifest.json`. All scripts are stdlib only.

## Pieces

- `rows.py`: row definitions (TMDB picks titles, IMDb dataset sorts; `MIN_RATING` 7.0, per-row vote floor, `BLOCK` for vote-stuffed titles).
  - **Genre vetting:** TMDB genres and keywords are loose, so every row that claims a genre is gated by IMDb `title.basics` genres: `imdb_genre` (one genre or a set, any of) and `imdb_without` (applies even with no `imdb_genre`). Dropdown genre tags are also kept only when IMDb confirms them (`CONFIRM` in build.py).
  - **Combined type:** `COMBINED` rows mix films and series under a custom "Combined" type in Discover (each item keeps its real type so it plays). `ids` = hand-picked titles (e.g. Interesting People); `merge` = joins existing rows; `split=True` alternates film/series so series don't crowd films out. `hidden=True` rows are built only to feed merges and are not listed.
- `build.py`: builds catalogs + manifest into `docs/` (committed). Shared helpers (`get`, `tmdb`, `imdb_ratings`, `PAGE`, `RPDB`) are imported by the other scripts. Manifest entries for watchlist and library rows live here.
- `watchlist.py <out>`: Liam's public IMDb watchlist as film/series rows, highest rated first. IMDb sits behind an AWS WAF challenge, so it reads through Jina Reader and retries until the parsed id count matches the page's own count. If Jina never delivers (it blocks anonymous imdb.com access for hours at a time), it copies the live Pages watchlist instead, so the rest of the build still deploys and no row goes empty. Optional `JINA_API_KEY` secret reads through Jina signed in, which avoids those blocks.
- `library.py <out>`: unwatched titles from Liam's Stremio Library ("Library (IMDb)" rows), highest rated first. Reads `api.strem.io/api/datastoreGet` with `STREMIO_AUTH_KEY`; "watched" = a film played to the end or marked watched (`timesWatched`/`flaggedWatched`); a series only once every released episode (Cinemeta, season > 0) is set in the `state.watched` bitfield. No key means empty rows, not a failure. It also strips every watched Library title (including removed and Continue Watching items) from the Watchlist and Foreign Watchlist (non-English) rows only (curated rows keep watched titles so Liam can rewatch), then repages so pages stay full, so it must run after `watchlist.py`.
- `push_manifest.py` (local, Mac only): pushes the live manifest into the Stremio account's addon collection so every device picks up new catalogs or resources without a reinstall. Reads the auth key from the Stremio Mac app's WebKit localStorage and backs up the collection to `~/.stremio_collection_backup.json` first. Run it after any manifest change has deployed.
- `episodes.py <out>`: per-episode IMDb ratings as a non-playable stream resource (shows with >= 5000 votes).

## Build and deploy

`.github/workflows/build.yml` runs daily 05:00 UTC, on push to main, and manually. It runs `build.py` and commits `docs/` + `cache/`, then copies `docs` to `_site`, adds watchlist, library and episodes output (~250k files, never committed) and deploys to Pages. It rebases before pushing so overlapping runs don't fail. Secrets: `TMDB_TOKEN`, `STREMIO_AUTH_KEY`, optional `JINA_API_KEY`.

Local: `TMDB_TOKEN=... python3 build.py` (optional `ROWS=id1,id2`).

## Gotchas

- Watchlist was briefly refreshed every 3 hours; now refreshed daily with everything else.
- TMDB `find` by IMDb id sometimes attaches a series' id to a film too, so `watchlist.meta` checks series first.
- If a run fails, the previous Pages deploy stays live.
- Watchlist: Jina returned HTTP 402 (Payment Required) from 6 Nov 2026, so the live copy is kept; likely the `JINA_API_KEY` is out of credit. The live-copy fallback retries Pages 503s.
- `gh run watch` can exit early; poll `gh run view <id> --json status` in an until-loop instead.
