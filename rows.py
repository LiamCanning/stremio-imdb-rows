"""Row definitions. Each row: TMDB discover filters pick the candidates,
IMDb ratings (rating >= MIN_RATING, votes >= min_votes) decide order.

home=True rows appear on the Stremio Home board; the rest are Discover only.
`recent_years` sets a rolling release-date window at build time.
"""

MIN_RATING = 7.0

# IMDb ids to drop from every row (mis-tagged on TMDB)
BLOCK = {"tt2592910"}  # CM101MMXI Fundamentals: stand-up special tagged documentary

# TMDB genre ids used in exclusions
ANIMATION, DOCUMENTARY, KIDS, MUSIC, NEWS, REALITY, TALK, TV_MOVIE = 16, 99, 10762, 10402, 10763, 10764, 10767, 10770
# sports documentary, sport, football, basketball, boxing, F1, tennis, Olympics, cycling, athlete
SPORT_KEYWORDS = "159290|333328|13042|6496|209476|233981|1488|2070|180491|274126"
NOT_REAL_TV = f"{ANIMATION},{REALITY},{TALK},{NEWS},{DOCUMENTARY}"

ROWS = [
    # --- Home ---
    dict(id="best_films", name="Best Films", type="movie", home=True, pages=150, min_votes=25000,
         params={}),
    dict(id="best_series", name="Best Series", type="series", home=True, pages=60, min_votes=20000,
         params={"without_genres": NOT_REAL_TV}),
    dict(id="best_new_films", name="Best New Films", type="movie", home=True, pages=40, min_votes=10000,
         recent_years=3, params={"without_genres": str(ANIMATION)}),
    dict(id="best_new_series", name="Best New Series", type="series", home=True, pages=30, min_votes=5000,
         recent_years=3, params={"without_genres": NOT_REAL_TV}),
    # --- Discover only ---
    dict(id="modern_classics", name="Modern Classics (1980-2009)", type="movie", pages=100, min_votes=25000,
         params={"primary_release_date.gte": "1980-01-01", "primary_release_date.lte": "2009-12-31"}),
    dict(id="classics", name="Classics (Pre-1980)", type="movie", pages=60, min_votes=10000,
         params={"primary_release_date.lte": "1979-12-31"}),
    dict(id="mind_bending", name="Mind-Bending Films", type="movie", pages=40, min_votes=10000,
         params={"with_keywords": "362567|326438|275311|3307|157171|12565|231173|10854|187008|3972|298527"}),
    dict(id="true_stories", name="True Stories", type="movie", pages=40, min_votes=10000,
         params={"with_keywords": "9672"}),
    dict(id="miniseries", name="Best Miniseries", type="series", pages=30, min_votes=5000,
         params={"with_type": "2", "without_genres": f"{DOCUMENTARY},{REALITY}"}),
    dict(id="hbo", name="Best of HBO", type="series", pages=20, min_votes=10000,
         params={"with_networks": "49", "without_genres": f"{REALITY},{TALK}"}),
    dict(id="british_series", name="Best British Series", type="series", pages=30, min_votes=5000,
         params={"with_origin_country": "GB", "without_genres": f"{DOCUMENTARY},{REALITY},{KIDS},{TALK},{NEWS}"}),
    dict(id="british_films", name="Best British Films", type="movie", pages=40, min_votes=25000,
         params={"with_origin_country": "GB", "without_genres": f"{DOCUMENTARY},{MUSIC}"}),
    dict(id="spanish_series", name="Best Spanish Series", type="series", pages=15, min_votes=1000,
         params={"with_origin_country": "ES", "with_original_language": "es", "without_genres": f"{ANIMATION},{KIDS},{DOCUMENTARY},{REALITY},{TALK}"}),
    dict(id="spanish_films", name="Best Spanish Films", type="movie", pages=20, min_votes=3000,
         params={"with_origin_country": "ES", "with_original_language": "es"}),
    dict(id="german_films", name="Best German Films", type="movie", pages=30, min_votes=10000,
         params={"with_origin_country": "DE", "with_original_language": "de"}),
    dict(id="biographies", name="Best Biopics", type="movie", pages=40, min_votes=20000,
         params={"with_keywords": "5565", "without_genres": str(DOCUMENTARY)}),
    dict(id="documentaries", name="Best Documentaries", type="movie", pages=40, min_votes=5000,
         params={"with_genres": str(DOCUMENTARY)}),
    dict(id="documentary_series", name="Best Documentary Series", type="series", pages=30, min_votes=3000,
         params={"with_genres": str(DOCUMENTARY), "without_genres": f"{REALITY},{TALK},{NEWS}"}),
    dict(id="sports_docs", name="Best Sports Documentaries", type="movie", pages=20, min_votes=1000,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": SPORT_KEYWORDS}),
    dict(id="sports_doc_series", name="Best Sports Documentary Series", type="series", pages=15, min_votes=500,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": SPORT_KEYWORDS}),
    dict(id="football_films", name="Best Football Films", type="movie", pages=15, min_votes=3000,
         params={"with_keywords": "13042"}, block={"tt31853193"}),  # Gundi (vote-stuffed)
    dict(id="football_series", name="Best Football Series", type="series", pages=10, min_votes=300,
         params={"with_keywords": "13042"}, block={"tt0141842"}),  # The Sopranos (mis-tagged)
    dict(id="korean_films", name="Best Korean Films", type="movie", pages=30, min_votes=10000,
         params={"with_origin_country": "KR", "with_original_language": "ko"}),
    dict(id="french_films", name="Best French Films", type="movie", pages=40, min_votes=15000,
         params={"with_origin_country": "FR", "with_original_language": "fr"}),
    dict(id="italian_films", name="Best Italian Films", type="movie", pages=30, min_votes=10000,
         params={"with_origin_country": "IT", "with_original_language": "it"}),
    dict(id="war_films", name="Best War Films", type="movie", pages=40, min_votes=25000,
         params={"with_genres": "10752"}),
    # English-language only keeps anime out; Klaus, Spider-Verse etc. are English originals
    dict(id="animated_films", name="Best Animated Films", type="movie", pages=40, min_votes=25000,
         params={"with_genres": str(ANIMATION), "with_original_language": "en"}),
    # Walt Disney Pictures, Pixar, Walt Disney Animation Studios
    dict(id="disney_pixar", name="Disney and Pixar", type="movie", pages=30, min_votes=25000,
         params={"with_companies": "2|3|6125"}),
]
