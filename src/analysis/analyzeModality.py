from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn
from pandas import DataFrame


def countModalities(df):
    all_modalities = (
        df["Modality"].dropna().str.split(",").explode().str.strip()
    )

    modalityCounts = all_modalities.value_counts().reset_index()
    modalityCounts.columns = ["Modality", "Count"]

    return modalityCounts


def plotModalities(modalityCounts):
    plt.figure(figsize=(12, 6))

    # bar plot with label
    plot = seaborn.barplot(
        data=modalityCounts, x="Modality", y="Count", palette="viridis"
    )
    for bar in plot.patches:  # Iterate over the individual bars
        bar_height = bar.get_height()
        plot.annotate(
            f"{int(bar_height)}",
            (bar.get_x() + bar.get_width() / 2, bar_height),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Modality", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Count of Modalities", fontsize=16)
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
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
        sheet_name="ModalityTable",
        engine="openpyxl",
    )
    df.columns = df.columns.str.strip()

    modalityCounts = countModalities(df)

    # Print the full DataFrame without truncation
    pandas.set_option("display.max_rows", None)

    plotModalities(modalityCounts)


if __name__ == "__main__":
    main()
