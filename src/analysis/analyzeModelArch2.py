from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def plotModelArch(df: DataFrame):
    aggregateDf = df.groupby("Architectural Family", as_index=False)[
        "Count"
    ].sum()

    # plt.figure(figsize=(8, 10))
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

    plt.show()


def plotModelArchByYear(df: DataFrame):
    groupedData = df.groupby(["Year", "Architectural Family"], as_index=False)[
        "Count"
    ].sum()

    sns.lineplot(
        data=groupedData,
        x="Year",
        y="Count",
        hue="Architectural Family",
        marker="o",
        palette="muted",
    )

    plt.title("Model Architectures Identified per Year", fontsize=16)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.legend(title="Architectural Family", loc="upper left")
    plt.tight_layout()

    plt.show()


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
def main(slr: Path) -> None:
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="Sheet2",
        engine="openpyxl",
    )
    # print(df.columns)
    plotModelArchByYear(df)


if __name__ == "__main__":
    main()
