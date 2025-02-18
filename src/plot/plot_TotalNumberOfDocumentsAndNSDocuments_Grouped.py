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
    "-d",
    "--documents",
    "documents",
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
    "-n",
    "--natural-science",
    "ns",
    nargs=1,
    required=True,
    help="Path to filtered journal documents from aius-filter-documents",
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
def main(
    documents: Path,
    ns: Path,
    outputPath: Path,
) -> None:
    """
    Process publication data from Parquet files and generate a bar plot
    showing the total number of PLOS publications per year.

    This function reads two Parquet files containing publication data,
    groups them by year, counts the number of publications in each category
    ('Total' and 'Natural Science'), and visualizes the data using a bar plot
    with a logarithmic y-scale.

    :param documents: The file path to the Parquet file containing total publication data.
    :type documents: Path
    :param ns: The file path to the Parquet file containing Natural Science publication data. # noqa:E501
    :type ns: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    stylePath = (
        Path(__file__).resolve().parents[2] / "styles" / "custom.mplstyle"
    )
    plt.style.use(stylePath)

    data: List[dict[str, int | str]] = []
    documentsDF: DataFrame = pandas.read_parquet(
        path=documents,
        engine="pyarrow",
    )
    nsDF: DataFrame = pandas.read_parquet(
        path=ns,
        engine="pyarrow",
    )

    documentsDF["publication_date"] = pandas.to_datetime(
        documentsDF["publication_date"]
    )

    nsDF["publication_date"] = pandas.to_datetime(nsDF["publication_date"])

    documentsDFGB: DataFrameGroupBy = documentsDF.groupby(
        by=documentsDF["publication_date"].dt.year
    )

    nsDFGB: DataFrameGroupBy = nsDF.groupby(
        by=nsDF["publication_date"].dt.year
    )

    idx: int
    _df: DataFrame
    for idx, _df in documentsDFGB:
        data.append({"year": idx, "amount": _df.shape[0], "class": "Total"})

    for idx, _df in nsDFGB:
        data.append(
            {"year": idx, "amount": _df.shape[0], "class": "Natural Science"}
        )

    df: DataFrame = DataFrame(data=data)

    sns.barplot(data=df, x="year", y="amount", palette="colorblind")
    plt.yscale("log")
    plt.title(label="Total Number of PLOS Publications From Search Results")
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Number of Publications")
    plt.tight_layout()
    plt.savefig(outputPath)


if __name__ == "__main__":
    main()
