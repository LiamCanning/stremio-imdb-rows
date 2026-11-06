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

# imdb_genre: the title must also carry this IMDb genre, or one of a set (and none of imdb_without), since TMDB genres are loose
# hidden: built only to feed a COMBINED merge; not listed under Movies or Series
UK_NORDIC = "GB|SE|DK|NO|IS|FI"
TRUE_CRIME_KEYWORDS = "33722|10714|161982"  # true crime, serial killer, murder investigation
# corporate scandal, wall street, business, finance, high finance, fraud, entrepreneur, economics, financial crisis, con artist
BUSINESS_KEYWORDS = "386332|5636|12094|246911|281170|4373|171068|14737|165193|10453"

ROWS = [
    # --- Home ---
    dict(id="best_films", name="Best Films", type="movie", home=True, pages=150, min_votes=25000,
         params={}),
    dict(id="best_series", name="Best Series", type="series", home=True, pages=60, min_votes=20000,
         params={"without_genres": NOT_REAL_TV}, imdb_without={"Reality-TV", "Talk-Show", "Game-Show"}),
    dict(id="best_new_films", name="Best New Films", type="movie", home=True, pages=40, min_votes=10000,
         recent_years=3, params={"without_genres": str(ANIMATION)}),
    dict(id="best_new_series", name="Best New Series", type="series", home=True, pages=30, min_votes=5000,
         recent_years=3, params={"without_genres": NOT_REAL_TV}),
    # --- Discover only (Discover lists each type's rows in this order) ---
    dict(id="comedy_films", name="Best Comedy Films", type="movie", pages=150, min_votes=10000,
         params={"with_genres": "35", "primary_release_date.gte": "1980-01-01",
                 # strict: no drama, crime, thriller, horror, mystery, war, history or action crossovers
                 "without_genres": f"{ANIMATION},{DOCUMENTARY},{MUSIC},18,80,53,27,9648,10752,36,28",
                 # no stand-up specials or short films
                 "without_keywords": "9716", "with_runtime.gte": "75"},
         imdb_genre="Comedy", imdb_without={"Drama", "Crime", "Thriller", "Horror", "Mystery", "War"}),
    dict(id="mind_bending", name="Mind-Bending Films", type="movie", pages=40, min_votes=10000,
         params={"with_keywords": "362567|326438|275311|3307|157171|12565|231173|10854|187008|3972|298527"},
         # plot-twist keywords catch straight crime dramas (Pulp Fiction, The Irishman) too
         imdb_genre={"Mystery", "Thriller", "Sci-Fi", "Fantasy"}),
    dict(id="modern_classics", name="Modern Classics (80s-00s)", type="movie", pages=100, min_votes=25000,
         params={"primary_release_date.gte": "1980-01-01", "primary_release_date.lte": "2009-12-31"}),
    dict(id="classics", name="Classics (Pre-1980)", type="movie", pages=60, min_votes=10000,
         params={"primary_release_date.lte": "1979-12-31"}),
    dict(id="war_films", name="Best War Films", type="movie", pages=40, min_votes=25000,
         params={"with_genres": "10752"}, imdb_genre="War"),
    dict(id="animated_films", name="Best Animated Films", type="movie", pages=40, min_votes=25000,
         params={"with_genres": str(ANIMATION)}, imdb_genre="Animation"),
    # Walt Disney Pictures, Pixar, Walt Disney Animation Studios
    dict(id="disney_pixar", name="Disney and Pixar", type="movie", pages=30, min_votes=25000,
         params={"with_companies": "2|3|6125"}),
    dict(id="true_stories", name="Based on True Events", type="movie", pages=40, min_votes=10000,
         params={"with_keywords": "9672", "without_genres": f"{ANIMATION},{DOCUMENTARY}"},
         imdb_without={"Documentary", "Horror", "Animation", "Sci-Fi"}),  # The Conjuring "true story" horror
    dict(id="biographies", name="Best Biopics", type="movie", pages=40, min_votes=20000,
         params={"with_keywords": "5565", "without_genres": str(DOCUMENTARY)}, imdb_genre="Biography"),
    dict(id="documentaries", name="Best Documentaries", type="movie", hidden=True, pages=40, min_votes=5000,
         params={"with_genres": str(DOCUMENTARY)}, imdb_genre="Documentary"),
    dict(id="sports_docs", name="Best Sports Documentaries", type="movie", hidden=True, pages=20, min_votes=1000,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": SPORT_KEYWORDS}, imdb_genre="Documentary"),
    dict(id="football_films", name="Best Football Films", type="movie", pages=15, min_votes=3000,
         params={"with_keywords": "13042", "without_genres": str(ANIMATION)}, block={"tt31853193"},  # Gundi (vote-stuffed)
         imdb_genre={"Sport", "Documentary"}, imdb_without={"Animation"}),  # TMDB "football" keyword is loose
    dict(id="british_films", name="Best British Films", type="movie", pages=40, min_votes=25000,
         params={"with_origin_country": "GB", "without_genres": f"{DOCUMENTARY},{MUSIC}"}),
    dict(id="spanish_films", name="Best Spanish Films", type="movie", pages=20, min_votes=3000,
         params={"with_origin_country": "ES", "with_original_language": "es"}),
    dict(id="spanish_docs", name="Spanish Documentaries", type="movie", pages=15, min_votes=200,
         params={"with_origin_country": "ES", "with_original_language": "es", "with_genres": str(DOCUMENTARY),
                 "without_keywords": SPORT_KEYWORDS},
         imdb_genre="Documentary", imdb_without={"Sport", "Music", "Musical"}),  # real life and history, not sport or music
    dict(id="french_films", name="Best French Films", type="movie", pages=40, min_votes=15000,
         params={"with_origin_country": "FR", "with_original_language": "fr"}),
    dict(id="italian_films", name="Best Italian Films", type="movie", pages=30, min_votes=10000,
         params={"with_origin_country": "IT", "with_original_language": "it"}),
    dict(id="german_films", name="Best German Films", type="movie", pages=30, min_votes=10000,
         params={"with_origin_country": "DE", "with_original_language": "de"}),
    dict(id="korean_films", name="Best Korean Films", type="movie", pages=30, min_votes=10000,
         params={"with_origin_country": "KR", "with_original_language": "ko"}),
    dict(id="miniseries", name="Best Miniseries", type="series", pages=30, min_votes=5000,
         params={"with_type": "2", "without_genres": f"{ANIMATION},{DOCUMENTARY},{REALITY}"},
         imdb_without={"Animation", "Documentary", "Reality-TV"}),
    dict(id="hbo", name="Best of HBO", type="series", pages=20, min_votes=10000,
         params={"with_networks": "49", "without_genres": f"{REALITY},{TALK}"}),
    dict(id="british_series", name="Best British Series", type="series", pages=30, min_votes=5000,
         params={"with_origin_country": "GB", "without_genres": f"{ANIMATION},{DOCUMENTARY},{REALITY},{KIDS},{TALK},{NEWS}"},
         imdb_without={"Animation", "Reality-TV", "Talk-Show", "Game-Show"}),  # no panel shows
    dict(id="spanish_series", name="Best Spanish Series", type="series", pages=15, min_votes=1000,
         params={"with_origin_country": "ES", "with_original_language": "es", "without_genres": f"{ANIMATION},{KIDS},{DOCUMENTARY},{REALITY},{TALK}"}),
    dict(id="spanish_doc_series", name="Spanish Documentary Series", type="series", pages=10, min_votes=100,
         params={"with_origin_country": "ES", "with_original_language": "es", "with_genres": str(DOCUMENTARY),
                 "without_genres": f"{REALITY},{TALK},{NEWS}", "without_keywords": SPORT_KEYWORDS},
         imdb_genre="Documentary", imdb_without={"Sport", "Music", "Musical"}),
    dict(id="documentary_series", name="Best Documentary Series", type="series", hidden=True, pages=30, min_votes=3000,
         params={"with_genres": str(DOCUMENTARY), "without_genres": f"{REALITY},{TALK},{NEWS}"}, imdb_genre="Documentary"),
    dict(id="sports_doc_series", name="Best Sports Documentary Series", type="series", hidden=True, pages=15, min_votes=500,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": SPORT_KEYWORDS}, imdb_genre="Documentary"),
    dict(id="football_series", name="Best Football Series", type="series", pages=10, min_votes=300,
         params={"with_keywords": "13042", "without_genres": str(ANIMATION)}, block={"tt0141842"},  # The Sopranos (mis-tagged)
         imdb_genre={"Sport", "Documentary"}, imdb_without={"Animation"}),
    # --- hidden sources for COMBINED merges ---
    dict(id="spanish_crime_films", name="Spanish Crime Films", type="movie", hidden=True, pages=15, min_votes=2000,
         params={"with_origin_country": "ES", "with_original_language": "es", "with_genres": "80|53|9648",
                 "without_genres": f"35,{ANIMATION},{DOCUMENTARY}"},
         imdb_genre={"Crime", "Thriller", "Mystery"}, imdb_without={"Comedy"}),
    dict(id="spanish_crime_series", name="Spanish Crime Series", type="series", hidden=True, pages=10, min_votes=500,
         params={"with_origin_country": "ES", "with_original_language": "es", "with_genres": "80|9648",
                 "without_genres": f"35,{ANIMATION},{DOCUMENTARY},{REALITY}"},
         imdb_genre={"Crime", "Thriller", "Mystery"}, imdb_without={"Comedy"},
         block={"tt6468322"}),  # La Casa de Papel: seen, not wanted
    dict(id="true_story_series", name="True Story Series", type="series", hidden=True, pages=15, min_votes=3000,
         params={"with_keywords": "9672", "without_genres": f"{ANIMATION},{DOCUMENTARY},{REALITY},{TALK}"}),
    dict(id="crime_films", name="Crime Films", type="movie", hidden=True, pages=30, min_votes=10000,
         params={"with_origin_country": UK_NORDIC, "with_genres": "80", "without_genres": f"35,{ANIMATION},{DOCUMENTARY}"},
         # no blockbuster co-productions (The Dark Knight Rises carries GB)
         imdb_genre="Crime", imdb_without={"Comedy", "Action", "Sci-Fi", "Fantasy"}),
    dict(id="crime_series", name="Crime Series", type="series", hidden=True, pages=20, min_votes=3000,
         params={"with_origin_country": UK_NORDIC, "with_genres": "80",
                 "without_genres": f"35,{ANIMATION},{DOCUMENTARY},{REALITY},{KIDS}"},
         imdb_genre="Crime", imdb_without={"Comedy"}),
    dict(id="true_crime_films", name="True Crime Films", type="movie", hidden=True, pages=15, min_votes=2000,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": TRUE_CRIME_KEYWORDS}, imdb_genre="Crime"),
    dict(id="true_crime_series", name="True Crime Series", type="series", hidden=True, pages=15, min_votes=1000,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": TRUE_CRIME_KEYWORDS,
                 "without_genres": f"{REALITY},{TALK},{NEWS}"}, imdb_genre="Crime"),
    dict(id="business_films", name="Business Films", type="movie", hidden=True, pages=15, min_votes=2000,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": BUSINESS_KEYWORDS}, imdb_genre="Documentary"),
    dict(id="business_series", name="Business Series", type="series", hidden=True, pages=10, min_votes=500,
         params={"with_genres": str(DOCUMENTARY), "with_keywords": BUSINESS_KEYWORDS,
                 "without_genres": f"{REALITY},{TALK},{NEWS}"}, imdb_genre="Documentary"),
]

# Rows that mix films and series under their own "Combined" type in Discover, highest IMDb rating first.
# ids: hand-picked titles (MIN_RATING does not apply); merge: the film and series rows above, joined;
# split: alternate films and series instead of pure rating order (series rate higher and would crowd films out).
COMBINED = [
    dict(id="interesting_people", name="Interesting People", ids=[
        # chefs and kitchens
        "tt2845786",   # Anthony Bourdain: Parts Unknown
        "tt4295140",   # Chef's Table
        "tt1772925",   # Jiro Dreams of Sushi
        "tt14512538",  # Roadrunner: A Film About Anthony Bourdain
        "tt0409608",   # Ramsay's Kitchen Nightmares (UK)
        "tt4125856",   # For Grace
        "tt2014351",   # Spinning Plates
        "tt2204371",   # Somm
        # fashion
        "tt6510332",   # McQueen
        "tt1621444",   # Bill Cunningham New York
        "tt2053352",   # Diana Vreeland: The Eye Has to Travel
        "tt18177528",  # The New Look
        "tt16024584",  # Cristóbal Balenciaga
        "tt11284244",  # Martin Margiela: In His Own Words
        "tt27052740",  # Becoming Karl Lagerfeld
        "tt3539664",   # Dior and I
        "tt1176244",   # Valentino: The Last Emperor
        "tt1331025",   # The September Issue
        "tt4157220",   # Iris
        "tt1606382",   # L'amour fou (Yves Saint Laurent)
        "tt2707858",   # Yves Saint Laurent
        "tt2707848",   # Saint Laurent
        "tt1035736",   # Coco Before Chanel
        "tt1023441",   # Coco Chanel & Igor Stravinsky
        "tt4378628",   # Westwood: Punk, Icon, Activist
        "tt11214590",  # House of Gucci
    ]),
    dict(id="combined_spanish_crime", name="Spanish Crime and Thrillers", merge=["spanish_crime_films", "spanish_crime_series"]),
    dict(id="combined_spain", name="Best of Spain", merge=["spanish_films", "spanish_series"]),
    dict(id="combined_spanish_docs", name="Spanish Documentaries", merge=["spanish_docs", "spanish_doc_series"]),
    dict(id="combined_true_story", name="Based on a True Story", merge=["true_stories", "biographies", "true_story_series"]),
    dict(id="combined_crime", name="Crime Dramas (UK and Nordic)", merge=["crime_films", "crime_series"]),
    dict(id="combined_true_crime", name="True Crime", merge=["true_crime_films", "true_crime_series"]),
    dict(id="combined_business", name="Business and Power", merge=["business_films", "business_series"]),
    dict(id="combined_docs", name="Best Documentaries", merge=["documentaries", "documentary_series"], split=True),
    dict(id="combined_sports_docs", name="Best Sports Documentaries", merge=["sports_docs", "sports_doc_series"]),
    dict(id="combined_football", name="Best Football", merge=["football_films", "football_series"]),
    dict(id="combined_british", name="Best of British", merge=["british_films", "british_series"], split=True),
]
