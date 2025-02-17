from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def plotModelArch(df: DataFrame, outputPath):
    aggregateDf = df.groupby("Architectural Family", as_index=False)[
        "Count"
    ].sum()

    sns.barplot(
        data=aggregateDf, x="Architectural Family", y="Count", palette="muted"
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
    df: DataFrame = pandas.read_excel(
        io=mdl,
        sheet_name="Sheet2",
        engine="openpyxl",
    )
    plotModelArch(df, outputPath)


if __name__ == "__main__":
    main()
