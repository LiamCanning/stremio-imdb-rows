# IMDb Rows

Static Stremio catalog addon. TMDB picks each row's titles, the IMDb ratings dataset sorts them (rating >= 7.0, per-row vote floor). Rebuilt every Monday by GitHub Actions and served from GitHub Pages (`docs/`).

- Rows: `rows.py`
- Build: `TMDB_TOKEN=... python3 build.py` (optional `ROWS=id1,id2`)
- Install URL: `https://liamcanning.github.io/stremio-imdb-rows/manifest.json`

If a weekly run fails, the previous week's files stay live.
