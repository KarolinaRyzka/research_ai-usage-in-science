from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
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


def plotIntervalTree(df, outputPath, ax=None):
    plt.style.use("ggplot")
    modalities = df["Modality"].unique()
    modality_to_y = {modality: idx for idx, modality in enumerate(modalities)}

    # Plot setup
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 12))

    # Plot intervals or dots
    for _, row in df.iterrows():
        year = row["Year Published"]
        modality = row["Modality"]
        count = row["Count"]
        y_pos = modality_to_y[modality]

        if count == 1:
            # dot for one
            ax.plot(year, y_pos, "ko", markersize=4)
            ax.text(
                year,
                y_pos + 0.1,
                f"{count}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        else:
            # line for >1
            ax.plot([year, year + 1], [y_pos, y_pos], "k-", lw=2)
            ax.text(
                year + 0.5,
                y_pos + 0.1,
                f"{count}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    # y axis is modality types
    ax.set_yticks(list(modality_to_y.values()))
    ax.set_yticklabels(list(modality_to_y.keys()))
    ax.set_xlabel("Year")
    ax.set_ylabel("Modality")
    ax.set_title("Modalities Distribution Over Years")
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
def main(slr: Path, outputPath) -> None:
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="ModalityTable",
        engine="openpyxl",
    )
    df.columns = df.columns.str.strip()

    modalityCounts = countModalitiesPerYear(df)
    plotIntervalTree(modalityCounts, outputPath)


if __name__ == "__main__":
    main()
