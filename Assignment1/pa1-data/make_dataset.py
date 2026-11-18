#!/usr/bin/env python3
"""
make_dataset.py - build a synthetic IMDB-style dataset for COMP7104 / DASC7104.

Three tables, the same schema as the lecture slides:

    actor(actor_id, first_name, last_name, birth_year)
    movie(movie_id, title, year, runtime_min, genre)
    casting(actor_id, movie_id, role, billing)

Everything is generated with DuckDB itself (no other dependency), deterministically,
and written as Parquet (for DuckDB) and CSV (for PostgreSQL COPY).

    python make_dataset.py                 # scale 1: 200k actors, 100k movies, 1M castings, ~40 MB
    python make_dataset.py --scale 5       # 5x bigger (1M actors, 500k movies, 5M castings)
    python make_dataset.py --out mydata    # write somewhere else

The generator guarantees that the lecture query (actors called Clint who played in 1995
movies) returns a few dozen rows at any scale.
"""
import argparse
import json
import os
import time

import duckdb

FIRST_NAMES = """
James John Robert Michael William David Richard Joseph Thomas Charles Christopher Daniel Matthew
Anthony Mark Donald Steven Paul Andrew Joshua Kenneth Kevin Brian George Timothy Ronald Edward Jason
Jeffrey Ryan Jacob Gary Nicholas Eric Jonathan Stephen Larry Justin Scott Brandon Benjamin Samuel
Gregory Alexander Frank Patrick Raymond Jack Dennis Jerry Tyler Aaron Jose Adam Nathan Henry Douglas
Zachary Peter Kyle Noah Ethan Jeremy Walter Christian Keith Roger Terry Austin Sean Gerald Carl Harold
Dylan Arthur Lawrence Jordan Jesse Bryan Billy Bruce Gabriel Joe Logan Alan Juan Albert Willie Elijah
Wayne Randy Vincent Mason Roy Ralph Eugene Russell Bobby Philip Louis Mary Patricia Jennifer Linda
Elizabeth Barbara Susan Jessica Sarah Karen Lisa Nancy Betty Sandra Margaret Ashley Kimberly Emily
Donna Michelle Carol Amanda Melissa Deborah Stephanie Dorothy Rebecca Sharon Laura Cynthia Amy Kathleen
Angela Shirley Brenda Emma Anna Pamela Nicole Samantha Katherine Christine Helen Debra Rachel Carolyn
Janet Maria Catherine Heather Diane Olivia Julie Joyce Victoria Ruth Virginia Lauren Kelly Christina
Joan Evelyn Judith Andrea Hannah Megan Cheryl Jacqueline Martha Madison Teresa Gloria Sara Janice Ann
Kathryn Abigail Sophia Frances Jean Alice Judy Isabella Julia Grace Amber Denise Danielle Marilyn
Beverly Charlotte Natalie Theresa Diana Brittany Doris Kayla Alexis Lori Marie Wei Li Ming Hui Mei
Jing Yan Ling Xiu Hao Kenji Yuki Haruto Sora Aiko Ravi Priya Arjun Ananya Omar Layla Amir Fatima
""".split()

LAST_NAMES = """
Eastwood Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez
Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez
Clark Ramirez Lewis Robinson Walker Young Allen King Wright Scott Torres Nguyen Hill Flores Green
Adams Nelson Baker Hall Rivera Campbell Mitchell Carter Roberts Gomez Phillips Evans Turner Diaz Parker
Cruz Edwards Collins Reyes Stewart Morris Morales Murphy Cook Rogers Gutierrez Ortiz Morgan Cooper
Peterson Bailey Reed Kelly Howard Ramos Kim Cox Ward Richardson Watson Brooks Chavez Wood James
Bennett Gray Mendoza Ruiz Hughes Price Alvarez Castillo Sanders Patel Myers Long Ross Foster Jimenez
Powell Jenkins Perry Russell Sullivan Bell Coleman Butler Henderson Barnes Gonzales Fisher Vasquez
Simmons Romero Jordan Patterson Alexander Hamilton Graham Reynolds Griffin Wallace Moreno West Cole
Hayes Bryant Herrera Gibson Ellis Tran Medina Aguilar Stevens Murray Ford Castro Marshall Owens
Harrison Fernandez McDonald Woods Washington Kennedy Wells Vargas Henry Chen Freeman Webb Tucker
Guzman Burns Crawford Olson Simpson Porter Hunter Gordon Mendez Silva Shaw Snyder Mason Dixon Munoz
Hunt Hicks Holmes Palmer Wagner Black Robertson Boyd Rose Stone Salazar Fox Warren Mills Meyer Rice
Schmidt Garza Daniels Ferguson Nichols Stephens Soto Weaver Ryan Gardner Payne Grant Dunn Kelley
Spencer Hawkins Arnold Pierce Vazquez Hansen Peters Santos Hart Bradley Knight Elliott Cunningham
Duncan Armstrong Hudson Carroll Lane Riley Andrews Alvarado Ray Delgado Berry Perkins Hoffman Johnston
Matthews Pena Richards Contreras Willis Carpenter Lawrence Sandoval Guerrero George Chapman Rios
Estrada Ortega Watkins Greene Nunez Wheeler Valdez Harper Burke Larson Santiago Maldonado Morrison
Franklin Carlson Austin Dominguez Carr Lawson Jacobs OBrien Lynch Singh Vidal Moreau Dubois Laurent
Zhang Wang Liu Yang Huang Zhao Wu Zhou Xu Sun Tanaka Suzuki Sato Yamamoto Nakamura Sharma Gupta
""".split()

TITLE_A = "The A Last First Dark Silent Broken Hidden Golden Red Black White Blue Lost Final Secret Endless Quiet Long Wild".split()
TITLE_B = "Harbour Road Night Summer River Garden City Empire Kingdom House Letter Storm Sky Ocean Mountain Bridge Train Station Hour Winter".split()
TITLE_C = ["of Shadows", "of Glass", "of Fire and Ice", "in Paris", "in Tokyo", "of Steel", "of Dreams", "Returns",
           "Rising", "Forever", "Reloaded", "Unbound", "Awakens", "of Sand", "at Dawn", "Underground", "in Hong Kong", "of the North"]
GENRES = "Drama Comedy Action Thriller Romance Documentary Horror Animation Crime Adventure SciFi Western".split()


def build(out_dir: str = "data", scale: float = 1.0, seed: int = 42, quiet: bool = False) -> dict:
    """Generate the three tables into out_dir. Returns row counts."""
    os.makedirs(out_dir, exist_ok=True)
    n_actors = int(200_000 * scale)
    n_movies = int(100_000 * scale)
    n_castings = int(1_000_000 * scale)
    t0 = time.time()
    con = duckdb.connect()
    con.execute(f"SELECT setseed({(seed % 1000) / 1000.0})")

    def lst(values):
        return "[" + ", ".join("'" + v.replace("'", "''") + "'" for v in values) + "]"

    con.execute(f"""
        CREATE TABLE actor AS
        SELECT CAST(i AS INTEGER) AS actor_id,
               -- about 1 actor in 400 is called Clint (the lecture query needs a rare-ish first name)
               CASE WHEN i % 397 = 0 THEN 'Clint' ELSE fn[1 + (i * 7919) % len(fn)] END AS first_name,
               ln[1 + (i * 104729) % len(ln)] AS last_name,
               1900 + ((i * 31 + (i // 7)) % 105) AS birth_year
        FROM (SELECT {lst(FIRST_NAMES)} AS fn, {lst(LAST_NAMES)} AS ln),
             range(1, {n_actors} + 1) t(i)
    """)
    con.execute(f"""
        CREATE TABLE movie AS
        SELECT CAST(i AS INTEGER) AS movie_id,
               ta[1 + (i * 13) % len(ta)] || ' ' || tb[1 + (i * 17) % len(tb)] || ' ' || tc[1 + (i * 19) % len(tc)] AS title,
               -- years 1900..2025, skewed towards recent decades
               CAST(1900 + floor(125 * pow(random(), 0.6)) AS INTEGER) AS year,
               CAST(70 + floor(random() * 90) AS INTEGER) AS runtime_min,
               g[1 + (i * 23) % len(g)] AS genre
        FROM (SELECT {lst(TITLE_A)} AS ta, {lst(TITLE_B)} AS tb, {lst(TITLE_C)} AS tc, {lst(GENRES)} AS g),
             range(1, {n_movies} + 1) t(i)
    """)
    # castings: each movie gets ~5-15 actors; popular actors (low ids) appear more often (power law)
    con.execute(f"""
        CREATE TABLE casting AS
        SELECT DISTINCT ON (movie_id, actor_id) actor_id, movie_id, role, billing FROM (
            SELECT CAST(1 + floor({n_actors} * pow(random(), 2.2)) AS INTEGER) AS actor_id,
                   CAST(1 + floor({n_movies} * random()) AS INTEGER) AS movie_id,
                   CASE WHEN random() < 0.7 THEN 'actor' WHEN random() < 0.5 THEN 'actress' ELSE 'self' END AS role,
                   CAST(1 + floor(random() * 15) AS INTEGER) AS billing
            FROM range({n_castings}) t(i)
        )
    """)
    counts = {}
    for tbl in ("actor", "movie", "casting"):
        con.execute(f"COPY {tbl} TO '{out_dir}/{tbl}.parquet' (FORMAT parquet)")
        con.execute(f"COPY {tbl} TO '{out_dir}/{tbl}.csv' (FORMAT csv, HEADER true)")
        counts[tbl] = con.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
    check = con.execute("""
        SELECT count(*) FROM actor a JOIN casting c USING (actor_id) JOIN movie m USING (movie_id)
        WHERE a.first_name = 'Clint' AND m.year = 1995
    """).fetchone()[0]
    con.close()
    json.dump({"scale": scale, "seed": seed, **counts, "clint_1995_rows": check}, open(f"{out_dir}/dataset.json", "w"))
    if not quiet:
        print(f"wrote {out_dir}/ in {time.time() - t0:.1f}s: "
              + ", ".join(f"{k}={v:,}" for k, v in counts.items())
              + f"; lecture query returns {check} rows")
    counts["clint_1995_rows"] = check
    counts["scale"] = scale
    return counts


def ensure(out_dir: str = "pa1data", scale=None, quiet: bool = False) -> dict:
    """Use the dataset in out_dir if it exists (and, when scale is given, has that scale); otherwise generate it.

    The lecture demos and PA1 all share one directory, pa1data. Demo 1 accepts whatever is there (scale=None, scale 1 if
    nothing exists); demos 2 and 3 and PA1 ask for scale 10, the size quoted on the slides, and regenerate if needed.
    """
    marker = f"{out_dir}/dataset.json"
    if os.path.exists(marker):
        info = json.load(open(marker))
        if scale is None or abs(info.get("scale", 0) - scale) < 1e-9:
            if not quiet:
                print(f"using {out_dir}/ (scale {info['scale']}: {info['casting']:,} castings)")
            return info
        if not quiet:
            print(f"{out_dir}/ holds scale {info['scale']}, regenerating at scale {scale}")
    return build(out_dir, scale if scale is not None else 1.0, quiet=quiet)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data", help="output directory (default: data)")
    ap.add_argument("--scale", type=float, default=1.0, help="size multiplier (default 1 = 1M castings)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    build(args.out, args.scale, args.seed)
