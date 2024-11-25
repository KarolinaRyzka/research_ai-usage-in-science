from itertools import product
from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame

from src.journals._generic import Journal_ABC
from src.journals.plos import PLOS
from src.search import RELEVANT_YEARS, SEARCH_QUERIES
from src.utils import ifFileExistsExit


def runCollector(journal: Journal_ABC) -> DataFrame:
    data: List[DataFrame] = []

    for pair in product(SEARCH_QUERIES, RELEVANT_YEARS):
        df: DataFrame = journal.searchJournal(query=pair[0], year=pair[1])
        data.append(df)

    df: DataFrame = pandas.concat(objs=data, ignore_index=True)

    df.drop_duplicates(
        subset=["url"],
        keep="first",
        inplace=True,
        ignore_index=True,
    )

    return df


@click.command()
@click.option(
    "-j",
    "--journal",
    "journal",
    required=False,
    type=click.Choice(choices=["plos"], case_sensitive=False),
    help="Journal to search for documents in",
    default="plos",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Output parquet file to save Pandas DataFrame to",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(outputPath: Path, journal: str) -> None:
    """
    Searches through a given journal and outputs a Pandas DataFrame stored as an Apache Parquet file with the search results.

    These search results are the raw outputs of the search meant to be post-processed for usage in other scripts.

    While the data outputted from this script can be leveraged independently, it is better to use this data in the following pipeline:

    **aius-search-journal** -> aius-extract-documents -> aius-filter-documents -> aius-sample-documents -> aius-download-documents
    """  # noqa: E501
    ifFileExistsExit(fps=[outputPath])

    journalClass: Journal_ABC
    match journal:
        case "plos":
            journalClass = PLOS()
        case _:
            exit(1)

    df: DataFrame = runCollector(journal=journalClass)

    df.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
