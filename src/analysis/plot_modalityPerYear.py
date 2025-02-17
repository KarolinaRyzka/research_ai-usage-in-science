from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def countModalitiesPerYear(df):
    df["Year Published"] = pandas.to_datetime(
        df["Year Published"], errors="coerce"
    ).dt.year

    exploded_df = (
        df.dropna(subset=["Modality", "Year Published"])
        .assign(Modality=df["Modality"].str.split(","))
        .explode("Modality")
    )
    exploded_df["Modality"] = exploded_df["Modality"].str.strip()

    modalityCounts = (
        exploded_df.groupby(["Year Published", "Modality"])
        .size()
        .reset_index(name="Count")
    )

    return modalityCounts


def plotModalitiesPerYear(modalityCountsDF, outputPath):
    palette = sns.color_palette("tab20", n_colors=len(modalityCountsDF))
    sns.lineplot(
        data=modalityCountsDF,
        x="Year Published",
        y="Count",
        hue="Modality",
        palette=palette,
    )

    plt.title("Total Counts of Data Modalities across the SLR by Year")
    plt.xlabel("Year")
    plt.ylabel("Total Count")
    plt.grid(True, linestyle="--", alpha=1)
    plt.tight_layout()
    plt.savefig(outputPath)


def wrapLabel(label, width=20):
    return "\n".join(label.split()[:2]) if len(label.split()) > 1 else label


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
        sheet_name="ModalityTable",
        engine="openpyxl",
    )
    df.columns = df.columns.str.strip()

    modalityCounts = countModalitiesPerYear(df)
    plotModalitiesPerYear(modalityCounts, outputPath)


if __name__ == "__main__":
    main()
