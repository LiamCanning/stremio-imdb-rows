# IMDb Rows (Stremio addon)

Static Stremio catalog addon served from GitHub Pages. Install: `https://liamcanning.github.io/stremio-imdb-rows/manifest.json`. All scripts are stdlib only.

## Pieces

- `rows.py`: row definitions (TMDB picks titles, IMDb dataset sorts; `MIN_RATING` 7.0, per-row vote floor, `BLOCK` for vote-stuffed titles).
- `build.py`: builds catalogs + manifest into `docs/` (committed). Shared helpers (`get`, `tmdb`, `imdb_ratings`, `PAGE`, `RPDB`) are imported by the other scripts. Manifest entries for watchlist and library rows live here.
- `watchlist.py <out>`: Liam's public IMDb watchlist as film/series rows, highest rated first. IMDb sits behind an AWS WAF challenge, so it reads through Jina Reader and retries until the parsed id count matches the page's own count; exits non-zero rather than deploy an empty row.
- `library.py <out>`: unwatched titles from Liam's Stremio Library ("Library (IMDb)" rows), highest rated first. Reads `api.strem.io/api/datastoreGet` with `STREMIO_AUTH_KEY`; "watched" = `timesWatched` or `flaggedWatched`. No key means empty rows, not a failure. It also strips every watched Library title (including removed and Continue Watching items) from all other rows in `<out>/catalog`, then repages each row and genre so pages stay full, so it must run after `watchlist.py`.
- `push_manifest.py` (local, Mac only): pushes the live manifest into the Stremio account's addon collection so every device picks up new catalogs or resources without a reinstall. Reads the auth key from the Stremio Mac app's WebKit localStorage and backs up the collection to `~/.stremio_collection_backup.json` first. Run it after any manifest change has deployed.
- `episodes.py <out>`: per-episode IMDb ratings as a non-playable stream resource (shows with >= 5000 votes).

## Build and deploy

`.github/workflows/build.yml` runs Mondays 05:00 UTC, on push to main, and manually. It runs `build.py` and commits `docs/` + `cache/`, then copies `docs` to `_site`, adds watchlist, library and episodes output (~250k files, never committed) and deploys to Pages. Secrets: `TMDB_TOKEN`, `STREMIO_AUTH_KEY`.

Local: `TMDB_TOKEN=... python3 build.py` (optional `ROWS=id1,id2`).

## Gotchas

- Watchlist was briefly refreshed every 3 hours; now weekly with everything else.
- TMDB `find` by IMDb id sometimes attaches a series' id to a film too, so `watchlist.meta` checks series first.
- If a run fails, last week's Pages deploy stays live.
