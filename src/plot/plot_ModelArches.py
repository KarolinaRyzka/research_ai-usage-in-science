from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def plotModelArch(df: DataFrame, outputPath: Path) -> None:
    """
    Generate and save a bar plot showing the total count of models by architecture type. # noqa:E501

    This function takes a DataFrame containing model architectures and their counts, # noqa:E501
    aggregates the data by architectural family, and produces a bar plot.

    :param df: A pandas DataFrame containing at least two columns:
               - 'Architectural Family': The category of the model architecture. # noqa:E501
               - 'Count': The frequency of models in each category.
    :type df: pandas.DataFrame
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    plt.style.use("ggplot")
    aggregateDf = df.groupby("Architectural Family", as_index=False)[
        "Count"
    ].sum()

    sns.barplot(
        data=aggregateDf,
        x="Architectural Family",
        y="Count",
        palette="colorblind",
    )

    for index, row in aggregateDf.iterrows():
        plt.text(
            x=index,
            y=row["Count"] + 0.1,
            s=row["Count"],
            ha="center",
            fontsize=10,
        )

    plt.title("Total Count of Models by Architecture Type", fontsize=16)
    plt.xlabel("Architecture Type", fontsize=12)
    plt.ylabel("Total Count", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(outputPath)


@click.command()
@click.option(
    "-m",
    "--m",
    "mdl",
    help="Path to model arch data",
    required=True,
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
def main(mdl: Path, outputPath: Path) -> None:
    """
    Process a model architecture dataset and generate a bar plot.

    This script reads a specified model architecture dataset from an Excel file, # noqa:E501
    extracts the relevant data, and generates a bar plot showing the total count of models # noqa:E501
    by architecture type. The plot is then saved to the specified output path.

    :param mdl: The file path to the model architecture dataset in Excel format. # noqa:E501
                The file must contain a sheet named 'Sheet2'.
    :type mdl: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    df: DataFrame = pandas.read_excel(
        io=mdl,
        sheet_name="Sheet2",
        engine="openpyxl",
    )
    plotModelArch(df, outputPath)


if __name__ == "__main__":
    main()
