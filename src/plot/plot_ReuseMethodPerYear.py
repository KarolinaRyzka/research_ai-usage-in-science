from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from pandas import DataFrame


def countReuse(df, column_name):
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


def plotReuseCount(df, outputPath):
    sns.barplot(data=df, x="Reuse Type", y="Count", palette="muted")

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
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="Form1",
        engine="openpyxl",
    )
    # df.columns = df.columns.str.strip()
    column_name = "What Is The Method Of PTM Re-Use Per Model?"
    reuseCounts = countReuse(df, column_name)
    plotReuseCount(reuseCounts, outputPath)


if __name__ == "__main__":
    main()
