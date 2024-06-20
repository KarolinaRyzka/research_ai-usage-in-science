from itertools import product
from pathlib import Path
from string import Template
from typing import List

import click
import pandas
from pandas import DataFrame
from pyfs import resolvePath

from aius.search import RELEVANT_YEARS, SEARCH_QUERIES, Journal_ABC
from aius.search.nature import Nature
from aius.search.plos import PLOS
from aius.search.science import Science

MEGA_JOURNAL_HELP_TEMPLATE: Template = Template(
    template="Search for documents in ${journal} mega journal",
)


def runCollector(journal: Journal_ABC) -> DataFrame:
    data: List[DataFrame] = []

    for pair in product(SEARCH_QUERIES, RELEVANT_YEARS):
        df: DataFrame = journal.conductSearch(query=pair[0], year=pair[1])
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
    "-o",
    "--output",
    "output",
    required=True,
    type=Path,
    help="Output pickle file to save Pandas DataFrame to",
)
@click.option(
    "-j",
    "--journal",
    "journal",
    required=True,
    type=click.Choice(choices=["nature", "plos", "science"]),
    help="Search for documents in a supported mega-journal",
)
def main(output: Path, journal: str) -> None:
    outputPath: Path = resolvePath(path=output)

    journalClass: Journal_ABC
    match journal:
        case "nature":
            journalClass = Nature()
        case "plos":
            journalClass = PLOS()
        case "science":
            journalClass = Science()
        case _:
            exit(1)

    df: DataFrame = runCollector(journal=journalClass)

    df.to_pickle(path=outputPath)


if __name__ == "__main__":
    main()