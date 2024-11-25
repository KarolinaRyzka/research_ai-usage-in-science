from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series

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
    help="Path to a transformed set of papers",
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
    help="Path to store data in CSV format",
)
def main(inputPath: Path, outputPath: Path) -> None:
    # 1. Check if output path already exists
    ifFileExistsExit(fps=[outputPath])

    # 2. Read in transformed documents
    print(f'Reading "{inputPath}"...')
    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")

    # 3. Extract relevant columns
    relevantDOI: DataFrame = df[["doi", "tags"]]
    explodedDF: DataFrame = relevantDOI.explode(
        column="tags",
        ignore_index=True,
    )
    explodedDF["tags"] = explodedDF["tags"].str.replace(pat='"', repl="")

    # 4. Count the tags
    tagCounts: Series = explodedDF.value_counts(subset="tags")

    # 5. Write results
    print(f'Writing "{outputPath}"...')
    tagCounts.to_csv(path_or_buf=outputPath)


if __name__ == "__main__":
    main()
