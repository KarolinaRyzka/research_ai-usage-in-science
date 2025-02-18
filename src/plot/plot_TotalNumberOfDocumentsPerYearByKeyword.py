from pathlib import Path
from typing import List

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
    showing the total number of PLOS publications per year, grouped by keyword.

    This function reads a Parquet file containing publication data, extracts
    search keywords from the query URL, groups publications by year and keyword, # noqa:E501
    counts the number of publications per group, and visualizes the results using # noqa:E501
    a bar plot.

    :param inputPath: The file path to the Parquet file containing publication data. # noqa:E501
    :type inputPath: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    stylePath = (
        Path(__file__).resolve().parents[2] / "styles" / "custom.mplstyle"
    )
    plt.style.use(stylePath)
    data: List[dict[int, str | int]] = []

    documentsDF: DataFrame = pandas.read_parquet(
        path=inputPath,
        engine="pyarrow",
    )

    documentsDF["keyword"] = documentsDF["queryURL"].apply(
        lambda x: x.split("&")[3].replace("q=", "").replace('"', "")
    )

    documentsDF["publication_date"] = pandas.to_datetime(
        documentsDF["publication_date"]
    )

    documentsDFGB: DataFrameGroupBy = documentsDF.groupby(
        by=documentsDF["publication_date"].dt.year
    )

    idx: int
    _df: DataFrame
    for idx, _df in documentsDFGB:
        keywordsDFGB: DataFrameGroupBy = _df.groupby(by="keyword")
        for _keyword, _keywordDF in keywordsDFGB:
            data.append(
                {
                    "year": idx,
                    "amount": _keywordDF.shape[0],
                    "Keyword": _keyword,
                }
            )

    df: DataFrame = DataFrame(data=data)

    sns.barplot(
        data=df, x="year", y="amount", hue="Keyword", palette="colorblind"
    )
    plt.title(
        label="Total Number of PLOS Publications From Search Results by Keyword"  # noqa:E501
    )
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Number of Publications")
    plt.tight_layout()

    plt.savefig(outputPath)


if __name__ == "__main__":
    main()
