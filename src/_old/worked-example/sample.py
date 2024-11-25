from pathlib import Path

import click
import pandas
from common import ifFileExistsExit, saveDFToJSON
from pandas import DataFrame


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    help="Path to mega journal search results (JSON)",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    help="Path to store sampled mega journal search results (JSON)",
    required=True,
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-s",
    "--sample",
    "sampleFrac",
    help="Sample amount (from 0 to 1)",
    required=False,
    type=float,
    default=0.5,
    show_default=True,
)
def main(
    inputPath: Path,
    outputPath: Path,
    sampleFrac: float = 0.5,
) -> None:
    ifFileExistsExit(fps=[outputPath])

    df: DataFrame = pandas.read_json(path_or_buf=inputPath)

    sampledDF: DataFrame = df.sample(
        frac=sampleFrac,
        replace=False,
        random_state=42,
        ignore_index=True,
    )

    saveDFToJSON(df=sampledDF, filename=outputPath)


if __name__ == "__main__":
    main()
