from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
from pandas import DataFrame


def countModalitiesPerYear(df: DataFrame) -> DataFrame:
    """
    Count the occurrences of each unique modality per year from the 'Modality' column in a DataFrame. # noqa:E501

    This function processes a pandas DataFrame by:

    - Converting the 'Year Published' column to a numeric year format.
    - Splitting multiple modalities within a single entry by commas.
    - Stripping any leading or trailing whitespace from each modality.
    - Grouping the data by 'Year Published' and 'Modality' to count occurrences. # noqa:E501

    :param df: A pandas DataFrame containing at least two columns:
               'Modality' (which may contain comma-separated modality names)
               and 'Year Published' (publication year as a string or numeric value). # noqa:E501
    :type df: pandas.DataFrame
    :return: A DataFrame with three columns: 'Year Published' (publication year), # noqa:E501
             'Modality' (unique modality names), and 'Count' (the number of occurrences per year). # noqa:E501
    :rtype: pandas.DataFrame
    """
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


def plotIntervalTree(df: DataFrame, outputPath: Path, ax=None) -> None:
    """
    Generate and save an interval plot showing the distribution of modalities over years. # noqa:E501

    This function visualizes the occurrence of different modalities over time.
    If a modality appears once in a given year, it is represented as a dot.
    If it appears multiple times, a horizontal line is drawn from that year to the next. # noqa:E501

    :param df: A pandas DataFrame containing at least three columns:
               - 'Year Published': The publication year of the modality.
               - 'Modality': The name of the modality.
               - 'Count': The frequency of the modality in that year.
    :type df: pandas.DataFrame
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :param ax: An optional Matplotlib axis object. If None, a new figure and axis will be created. # noqa:E501
    :type ax: matplotlib.axes.Axes, optional
    :return: None. The function saves the plot to the specified output file and does not return any value. # noqa:E501
    :rtype: None
    """
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


def wrapLabel(label: str, width=20) -> str:
    """
    Wrap a label into multiple lines if it contains more than one word.

    This function splits the label by whitespace and joins the first two words with a newline character. # noqa:E501
    If the label contains only one word, it is returned unchanged.

    :param label: The input label to be wrapped.
    :type label: str
    :param width: The maximum width of the label (currently unused but can be extended for future functionality). # noqa:E501
    :type width: int, optional
    :return: The wrapped label with at most two words on the first line, separated by a newline if needed. # noqa:E501
    :rtype: str
    """
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
    """
    Process an SLR results file, extract modality data per year, and generate an interval plot. # noqa:E501

    This script reads a specified SLR (Systematic Literature Review) results file in Excel format, # noqa:E501
    extracts the 'Modality' column from the "ModalityTable" sheet, counts unique modalities per year, # noqa:E501
    and generates an interval plot showing their distribution over time. The plot is then saved to the # noqa:E501
    specified output path.

    :param slr: The file path to the SLR results in Excel format. It must contain a sheet named 'ModalityTable'. # noqa:E501
    :type slr: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
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
