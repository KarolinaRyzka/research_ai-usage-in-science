from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from pandas import DataFrame


def countReuse(df: DataFrame, column_name: str) -> DataFrame:
    """
    Count occurrences of specific reuse types in a given column of a DataFrame.

    This function scans a column for occurrences of the reuse types: 'adaptation', # noqa:E501
    'conceptual', and 'deployment', performing a case-insensitive match. It returns # noqa:E501
    a DataFrame with counts for each reuse type.

    :param df: A pandas DataFrame containing textual data.
    :type df: pandas.DataFrame
    :param column_name: The name of the column in which to search for reuse types. # noqa:E501
    :type column_name: str
    :return: A DataFrame with two columns:
             - 'Reuse Type': The type of reuse detected.
             - 'Count': The number of occurrences of each reuse type.
    :rtype: pandas.DataFrame
    """
    # Initialize a dictionary to store counts
    reuse_counts = {"adaptation": 0, "conceptual": 0, "deployment": 0}

    # Extract the column and count occurrences
    for cell in df[column_name]:
        if pd.notna(cell):  # Check for non-empty cells
            cell = (
                cell.lower()
            )  # Convert to lowercase for case-insensitive matching
            for reuse_type in reuse_counts.keys():
                reuse_counts[reuse_type] += cell.count(reuse_type)

    # Convert the counts to a pandas DataFrame
    result_df = pd.DataFrame(
        list(reuse_counts.items()), columns=["Reuse Type", "Count"]
    )
    return result_df


def plotReuseCount(df: DataFrame, outputPath: Path) -> None:
    """
    Generate and save a bar plot showing the total count of reuse methods for DL models identified in the SLR. # noqa:E501

    This function takes a DataFrame containing reuse method counts, creates a bar plot using Seaborn, # noqa:E501
    and labels each bar with its corresponding count. The x-axis labels are formatted with # noqa:E501
    title case for readability.

    :param df: A pandas DataFrame containing at least two columns:
               - 'Reuse Type': The type of reuse (e.g., 'adaptation', 'conceptual', 'deployment'). # noqa:E501
               - 'Count': The frequency of each reuse method in the dataset.
    :type df: pandas.DataFrame
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    stylePath = (
        Path(__file__).resolve().parents[2] / "styles" / "custom.mplstyle"
    )
    plt.style.use(stylePath)
    sns.barplot(data=df, x="Reuse Type", y="Count", palette="colorblind")

    for index, row in df.iterrows():
        plt.text(
            x=index,
            y=row["Count"] + 0.1,
            s=row["Count"],
            ha="center",
            fontsize=10,
        )

    plt.title(
        "Total Count of Reuse Methods used for DL Models indentified in the SLR",  # noqa: E501
        fontsize=16,
    )
    plt.xlabel("Reuse Method", fontsize=12)
    plt.ylabel("Total Count", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    ax = plt.gca()
    ax.set_xticklabels([label.title() for label in df["Reuse Type"]])
    plt.tight_layout()
    plt.savefig(outputPath)


@click.command()
@click.option(
    "-s",
    "--slr",
    "slr",
    help="Path to SLR results",
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
def main(slr: Path, outputPath: Path) -> None:
    """
    Process an SLR dataset to count occurrences of pre-trained model reuse methods # noqa:E501
    and generate a bar plot.

    This function reads an Excel file containing information about the reuse methods # noqa:E501
    of pre-trained models, counts occurrences of reuse types ('adaptation', 'conceptual', # noqa:E501
    'deployment'), and visualizes the results using a bar plot.

    :param slr: The file path to the SLR dataset in Excel format.
                The file must contain a sheet named 'Form1' with a column specifying reuse methods. # noqa:E501
    :type slr: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="Form1",
        engine="openpyxl",
    )
    column_name = "What Is The Method Of PTM Re-Use Per Model?"
    reuseCounts = countReuse(df, column_name)
    plotReuseCount(reuseCounts, outputPath)


if __name__ == "__main__":
    main()
