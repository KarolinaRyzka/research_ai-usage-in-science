from pathlib import Path

import click
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas
import seaborn as sns
from pandas import DataFrame


def countModalities(df):
    all_modalities = (
        df["Modality"].dropna().str.split(",").explode().str.strip()
    )

    modalityCounts = all_modalities.value_counts().reset_index()
    modalityCounts.columns = ["Modality", "Count"]

    return modalityCounts


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


def plotModalitiesPerYear(modalityCountsDF):
    palette = sns.color_palette("tab20", n_colors=len(modalityCountsDF))
    plot = sns.barplot(
        data=modalityCountsDF,
        x="Year Published",
        y="Count",
        hue="Modality",
        palette=palette,
    )

    for bar in plot.patches:
        bar_height = bar.get_height()
        if bar_height > 0:
            plot.annotate(
                f"{int(bar_height)}",
                (bar.get_x() + bar.get_width() / 2, bar_height),
                ha="center",
                va="bottom",
                fontsize=10,
                color="black",
            )

    plt.title("Total Counts of Data Modalities across the SLR by Year")
    plt.xlabel("Year")
    plt.ylabel("Total Count")
    plt.tight_layout()
    plt.show()


def plotModalities(modalityCounts):
    # plt.figure(figsize=(8, 10))
    palette = sns.color_palette("tab20", n_colors=len(modalityCounts))

    plot = sns.barplot(
        data=modalityCounts, x="Count", y="Modality", palette=palette
    )

    # Add labels on the bars
    for bar in plot.patches:  # Iterate over the bars
        bar_width = bar.get_width()  # Get the width (horizontal bar)
        plot.annotate(
            f"{int(bar_width)}",  # Text to display
            (
                bar_width + 0.2,
                bar.get_y() + bar.get_height() / 2,
            ),  # Position: slightly right of the bar
            ha="left",
            va="center",
            fontsize=10,
            color="black",
        )

    # Customize labels and title
    plt.xlabel("Count")
    plt.ylabel("Modality")
    plt.title("Total Counts of Data Modalities across the SLR")
    plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    plt.tight_layout()  # Adjust layout to fit everything nicely

    # Show the plot
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

    # modalityCounts = countModalities(df)
    modalitiesPerYear = countModalitiesPerYear(df)

    # Print the full DataFrame without truncation
    pandas.set_option("display.max_rows", None)

    plotModalitiesPerYear(modalitiesPerYear)
    # plotModalities(modalityCounts)


if __name__ == "__main__":
    main()
