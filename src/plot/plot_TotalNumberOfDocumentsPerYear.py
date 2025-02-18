from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    nargs=1,
    required=True,
    help="Path to non-filtered journal documents from aius-extract-documents",
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
    nargs=1,
    required=True,
    help="Path to write figure to",
    type=click.Path(
        exists=False,
        file_okay=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(inputPath: Path, outputPath: Path) -> None:
    """
    Process publication data from a Parquet file and generate a bar plot
    showing the total number of PLOS publications per year.

    This function reads a Parquet file containing publication data,
    groups the data by year, counts the number of publications per year,
    and visualizes the results using a bar plot.

    :param inputPath: The file path to the Parquet file containing publication data. # noqa:E501
    :type inputPath: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    plt.style.use("ggplot")
    data: dict[int, int] = {}

    df: DataFrame = pandas.read_parquet(
        path=inputPath,
        engine="pyarrow",
    )

    df["publication_date"] = pandas.to_datetime(df["publication_date"])

    dfgb: DataFrameGroupBy = df.groupby(by=df["publication_date"].dt.year)

    idx: int
    _df: DataFrame
    for idx, _df in dfgb:
        data[idx] = _df.shape[0]

    sns.barplot(data=data, palette="colorblind")
    plt.title(label="Total Number of PLOS Publications From Search Results")
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Number of Publications")
    plt.tight_layout()

    plt.savefig(outputPath)


if __name__ == "__main__":
    main()
