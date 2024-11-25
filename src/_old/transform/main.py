from pathlib import Path
from typing import List

import click
import pandas
from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from progress.bar import Bar

from src.classes.journalGeneric import Journal_ABC
from src.classes.plos import PLOS
from src.utils import ifFileExistsExit


def extractContent(df: DataFrame, journal: Journal_ABC) -> DataFrame:
    data: dict[str, List[str]] = {
        "doi": [],
        "url": [],
        "titles": [],
        "abstracts": [],
        "content": [],
        "tags": [],
    }

    with Bar("Extracting content from HTML...", max=df.shape[0]) as bar:
        row: Series
        for _, row in df.iterrows():
            data["doi"].append(row["doi"])
            data["url"].append(row["url"])

            soup: BeautifulSoup = BeautifulSoup(
                markup=row["html"],
                features="lxml",
            )

            data["titles"].append(journal.extractTitleFromPaper(soup=soup))
            data["abstracts"].append(
                journal.extractAbstractFromPaper(soup=soup)
            )
            data["content"].append(journal.extractContentFromPaper(soup=soup))

            # TODO: Add support for extracting OA Tags
            data["tags"].append(journal.extractJournalTagsFromPaper(soup=soup))

            bar.next()

    return DataFrame(data=data)


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
    help="Path to downloaded academic papers",
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

    df: DataFrame = pandas.read_parquet(path=inputPath)

    foo: DataFrame = df[df["status_code"] == 200]

    extractContent(df=foo, journal=PLOS()).to_parquet(
        path=outputPath,
        engine="pyarrow",
    )


if __name__ == "__main__":
    main()
