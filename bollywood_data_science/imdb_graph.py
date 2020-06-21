import asyncio
import subprocess
import tempfile
import urllib.parse
from pathlib import Path
from typing import Set

import aiofiles
import aiohttp
import charmonium.cache as ch_cache
import charmonium.time_block as ch_time_block
import rdflib
from imdb import IMDb
from tqdm import tqdm


async def download_url(session: aiohttp.ClientSession, url: str, path: Path) -> None:
    with ch_time_block.ctx(f"Download {path.name}"):
        async with session.get(url) as source_fobj:
            async with aiofiles.open(path, "w+") as dest_fobj:
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


@ch_cache.decor(ch_cache.FileStore.create("tmp"))
def download_imdb(cache_path: Path) -> str:
    with tempfile.TemporaryDirectory() as tmp_path_:
        tmp_path = Path(tmp_path_)

        async def async_part() -> None:
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(
                    *[
                        download_url(
                            session,
                            url,
                            tmp_path / Path(urllib.parse.urlparse(url).path).name,
                        )
                        for url in imdb_source_urls
                    ]
                )

        asyncio.run(async_part())
        db_url = "sqlite:///{cache_path / 'imdb.sqlite'}"
        subprocess.run(
            ["s32imdbpy.py", str(cache_path), db_url], check=True,
        )
        return db_url


def imdb_graph(imdb_ids: Set[str]) -> rdflib.Graph:
    download_imdb(Path("tmp"))
    ia = IMDb("s3", "postgres://user:password@localhost/imdb")
    graph = rdflib.Graph()
    imdb_ns = rdflib.Namespace("https://imdb.com/")

    for imdb_id in tqdm(imdb_ids):
        person = ia.get_person(imdb_id[2:])
        person_term = rdflib.Literal(imdb_id)

        for filmography in person.get("filmography", {}):
            for role in filmography.keys():
                for movie in filmography.get(role, []):
                    graph.add(
                        (
                            person_term,
                            imdb_ns.term(f"filmography/{role}"),
                            rdflib.Literal(f"tt{movie.movieID}"),
                        )
                    )

        for award in person.get("awards", []):
            graph.add((person_term, imdb_ns.term("award"), rdflib.Literal(award),))

        for trademark in person.get("trademarks", []):
            graph.add(
                (person_term, imdb_ns.term("trademark"), rdflib.Literal(trademark),)
            )

    return graph
