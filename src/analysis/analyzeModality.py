from pathlib import Path

import click
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas
import seaborn as sns
from pandas import DataFrame


def countModalities(df):
    all_modalities = (
        df["Modality"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()  # split up items in cell by ",""
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
    # split data
    modalityCounts = modalityCountsDF.groupby("Modality")["Count"].count()
    singleModalities = modalityCounts[modalityCounts == 1].index
    multipleModalities = modalityCounts[modalityCounts > 1].index

    # Set up the palette
    palette = sns.color_palette(
        "tab20", n_colors=len(modalityCountsDF["Modality"].unique())
    )

    # line plot for modalities that occur more than once
    plt.figure(figsize=(12, 8))
    sns.lineplot(
        data=modalityCountsDF[
            modalityCountsDF["Modality"].isin(multipleModalities)
        ],
        x="Year Published",
        y="Count",
        hue="Modality",
        palette=palette,
        legend="full",
    )

    # scatter plot for single modalities
    sns.scatterplot(
        data=modalityCountsDF[
            modalityCountsDF["Modality"].isin(singleModalities)
        ],
        x="Year Published",
        y="Count",
        hue="Modality",
        palette=palette,
        legend=False,
        s=50,  # Size of the scatter points
        marker="o",
    )

    plt.title("Total Counts of Data Modalities across the SLR by Year")
    plt.xlabel("Year Published")
    plt.ylabel("Total Count")
    plt.grid(True, linestyle="--", alpha=1)
    plt.tight_layout()
    plt.show()


def plotModalitiesPerYear2(modalityCountsDF):
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
    plt.show()


def plotModalities(modalityCounts):
    palette = sns.color_palette("tab20", n_colors=len(modalityCounts))
    dfSorted = modalityCounts.sort_values(by="Count", ascending=False).head(5)

    plot = sns.barplot(data=dfSorted, x="Count", y="Modality", palette=palette)

    # Add labels on the bars
    for bar in plot.patches:  # Iterate over the bars
        bar_width = bar.get_width()  # Get the width (horizontal bar)
        plot.annotate(
            f"{int(bar_width)}",  # Text to display
            (
                bar_width,
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
    plt.title("Top 5 Modalities identified across the SLR")
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

    plotModalitiesPerYear2(modalitiesPerYear)
    # plotModalities(modalityCounts)


if __name__ == "__main__":
    main()
