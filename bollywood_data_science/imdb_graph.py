import asyncio
import subprocess
import urllib.parse
from pathlib import Path
from typing import Iterable, Tuple

import aiofiles
import aiohttp
import charmonium.cache as ch_cache
import charmonium.time_block as ch_time_block
import rdflib
from imdb import IMDb
from tqdm import tqdm


async def download_url(session: aiohttp.ClientSession, url: str, path: Path) -> None:
    if not path.exists():
        with ch_time_block.ctx(f"download {path.name}"):
            async with session.get(url) as source_fobj:
                async with aiofiles.open(path, "wb+") as dest_fobj:
                    await dest_fobj.write(await source_fobj.read())


imdb_source_urls = [
    "https://datasets.imdbws.com/name.basics.tsv.gz",
    "https://datasets.imdbws.com/title.akas.tsv.gz",
    "https://datasets.imdbws.com/title.basics.tsv.gz",
    "https://datasets.imdbws.com/title.crew.tsv.gz",
    "https://datasets.imdbws.com/title.episode.tsv.gz",
    "https://datasets.imdbws.com/title.principals.tsv.gz",
    "https://datasets.imdbws.com/title.ratings.tsv.gz",
]


def download_imdb(cache_path: Path) -> str:
    async def async_part() -> None:
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[
                    download_url(
                        session,
                        url,
                        cache_path / Path(urllib.parse.urlparse(url).path).name,
                    )
                    for url in imdb_source_urls
                ]
            )

    asyncio.run(async_part())
    # db_url = f"sqlite:///{cache_path / 'imdb.sqlite'}"
    db_url = "postgresql://postgres:pass@localhost/imdb"
    print(db_url)
    subprocess.run(
        ["s32imdbpy.py", "--verbose", str(cache_path), db_url], check=True,
    )
    return db_url


@ch_cache.decor(ch_cache.DirectoryStore.create("tmp"), verbose=True)
def imdb_graph(
    imdb_ids: Iterable[Tuple[rdflib.term.Node, str]], db: bool
) -> rdflib.Graph:
    if db:
        db_url = download_imdb(Path("tmp"))
        ia = IMDb("s3", db_url)
    else:
        ia = IMDb()
    graph = rdflib.Graph()
    imdb_ns = rdflib.Namespace("https://imdb.com/")

    for person_term, imdb_id in tqdm(imdb_ids):
        person = ia.get_person(imdb_id[2:])

        dates = []
        filmography = person.get("filmography", {})
        if True:
            if not isinstance(filmography, dict):
                raise TypeError(repr(type(filmography)))
            for role in filmography.keys():
                for movie in filmography.get(role, []):
                    graph.add(
                        (
                            person_term,
                            imdb_ns.term(f"filmography_{role.replace(' ' , '_')}"),
                            rdflib.Literal(f"tt{movie.movieID}"),
                        )
                    )
                    if "year" in movie:
                        dates.append(movie["year"])

        if "filmography" not in person.keys():
            print(f"No filmography for person {imdb_id}")

        if dates:
            graph.add(
                (person_term, imdb_ns.term("work_start"), rdflib.Literal(min(dates)))
            )
            graph.add(
                (person_term, imdb_ns.term("work_stop"), rdflib.Literal(max(dates)))
            )

        for award in person.get("awards", []):
            graph.add((person_term, imdb_ns.term("award"), rdflib.Literal(award),))

        for trademark in person.get("trademarks", []):
            graph.add(
                (person_term, imdb_ns.term("trademark"), rdflib.Literal(trademark),)
            )

        if "birth date" in person:
            graph.add(
                (
                    person_term,
                    imdb_ns.term("birth_date"),
                    rdflib.Literal(person["birth date"], datatype=rdflib.XSD.date),
                )
            )

        if "death date" in person:
            graph.add(
                (
                    person_term,
                    imdb_ns.term("death_date"),
                    rdflib.Literal(person["death date"], datatype=rdflib.XSD.date),
                )
            )

        if "name" in person:
            graph.add(
                (person_term, imdb_ns.term("name"), rdflib.Literal(person["name"]))
            )
        elif "canonical name" in person:
            graph.add(
                (
                    person_term,
                    imdb_ns.term("name"),
                    rdflib.Literal(person["canonical name"]),
                )
            )

    return graph
