from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response

from src.classes.search import Search
from src.utils import ifFileExistsExit


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a filtered list of academic papers",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to save journal paper parquet file",
)
def main(inputPath: Path, outputPath: Path) -> None:
    ifFileExistsExit(fps=[outputPath])

    data: dict[str, List[str | int | bytes]] = {
        "doi": [],
        "url": [],
        "status_code": [],
        "html": [],
    }

    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")

    with Bar("Downloading papers...", max=df.shape[0]) as bar:
        row: Series
        for _, row in df.iterrows():
            search: Search = Search()

            data["doi"].append(row["doi"])

            resp: Response | None = search.search(url=row["doi"])

            if resp is None:
                data["url"].append(row["doi"])
                data["status_code"].append(404)
                data["html"].append("")
                bar.next()
                continue

            data["url"].append(resp.url)
            data["status_code"].append(resp.status_code)
            data["html"].append(resp.content.decode(errors="ignore"))

            bar.next()

    outputDF: DataFrame = DataFrame(data=data)
    outputDF.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
