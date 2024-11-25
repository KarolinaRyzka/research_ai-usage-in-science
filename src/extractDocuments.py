from json import loads
from pathlib import Path
from typing import Any, List

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar

from src.utils import ifFileExistsExit


def extractDocuments(df: DataFrame) -> DataFrame:
    # NOTE: This is currently only applicable to PLOS search results

    data: List[DataFrame] = []

    with Bar(
        "Extracting documents from search results...", max=df.shape[0]
    ) as bar:
        row: Series
        for _, row in df.iterrows():
            searchResultsMetadata: dict[str, Any] = loads(row["html"])[
                "searchResults"
            ]

            if searchResultsMetadata["numFound"] == 0:
                bar.next()
                continue

            docsDF: DataFrame = DataFrame(searchResultsMetadata["docs"])

            docsDF["queryURL"] = row["url"]

            docsDF["doi"] = docsDF["id"].apply(
                lambda x: f"https://doi.org/{x}",
            )

            data.append(docsDF)

            bar.next()

    return pandas.concat(objs=data, ignore_index=True)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    required=True,
    help="Journal search results in Apache Parquet format",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Apache Parquet file to write to containing search result documents",
    type=click.Path(
        exists=False,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(inputPath: Path, outputPath: Path) -> None:
    """
    Given the search results of a journal, output a Pandas DataFrame that organizes the metadata of each document as reported by the journal stored as an Apache Parquet file with the search results.

    These search results are the raw outputs of the search meant to be post-processed for usage in other scripts.

    While the data outputted from this script can be leveraged independently, it is better to use this data in the following pipeline:

    aius-search-journal -> **aius-extract-documents** -> aius-filter-documents -> aius-sample-documents -> aius-download-documents
    """  # noqa: E501

    ifFileExistsExit(fps=[outputPath])

    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")

    docsDF: DataFrame = extractDocuments(df=df)

    docsDF.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
