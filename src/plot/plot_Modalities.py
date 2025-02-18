from pathlib import Path

import click
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas
import seaborn as sns
from pandas import DataFrame


def countModalities(df: DataFrame) -> DataFrame:
    """
    Count the occurrences of each unique modality in the 'Modality' column of a DataFrame. # noqa:E501

    This function processes a pandas DataFrame by:

    - Extracting non-null values from the 'Modality' column.
    - Splitting multiple modalities within a single entry by commas.
    - Stripping any leading or trailing whitespace from each modality.
    - Counting the occurrences of each unique modality.

    :param df: A pandas DataFrame containing a column named 'Modality'. Each entry may contain # noqa:E501
               one or multiple comma-separated modality names.
    :type df: pandas.DataFrame
    :return: A DataFrame with two columns: 'Modality' (unique modality names) and 'Count' (the number of occurrences). # noqa:E501
    :rtype: pandas.DataFrame
    """
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


def wrapLabel(label: str, width=20) -> str:
    """
    Wrap a label into multiple lines if it contains more than one word.

    This function splits the label by whitespace and joins the first two words with a newline character. # noqa:E501
    If the label contains only one word, it is returned unchanged.

    :param label: The input label to be wrapped.
    :type label: str
    :param width: The maximum width of the label (currently unused but can be extended for future functionality). # noqa:E501
    :type width: int, optional
    :return: The wrapped label with at most two words on the first line, separated by a newline if needed.
    :rtype: str
    """
    return "\n".join(label.split()[:2]) if len(label.split()) > 1 else label


def plotModalities(modalityCounts, outputPath) -> None:
    """
    Generate and save a bar plot of the top 5 most frequent modalities.

    This function sorts the given DataFrame by the 'Count' column in descending order, # noqa:E501
    selects the top 5 modalities, and creates a horizontal bar plot using Seaborn. # noqa:E501
    The y-axis labels are wrapped for better readability, and the count values are annotated on the bars. # noqa:E501

    :param modalityCounts: A pandas DataFrame containing at least two columns:
                           'Modality' (category labels) and 'Count' (frequency of each modality). # noqa:E501
    :type modalityCounts: pd.DataFrame
    :param outputPath: The file path where the generated plot will be saved.
    :type outputPath: str
    :return: None. The function saves the plot to the specified output file and does not return any value. # noqa:E501
    :rtype: None
    """

    stylePath = (
        Path(__file__).resolve().parents[2] / "styles" / "custom.mplstyle"
    )
    plt.style.use(stylePath)
    dfSorted = modalityCounts.sort_values(by="Count", ascending=False).head(5)

    # Apply the wrapping function to the y-axis labels
    dfSorted["Modality"] = dfSorted["Modality"].apply(wrapLabel)

    plot = sns.barplot(
        data=dfSorted, x="Count", y="Modality", palette="colorblind"
    )

    # Add labels on the bars
    for bar in plot.patches:
        bar_width = bar.get_width()
        plot.annotate(
            f"{int(bar_width)}",
            (
                bar_width,
                bar.get_y() + bar.get_height() / 2,
            ),  # Position: slightly right of the bar
            ha="left",
            va="center",
            fontsize=10,
            color="black",
        )

    plt.xlabel("Count")
    plt.ylabel("Modality", labelpad=20)
    plt.title("Top 5 Modalities identified across the SLR")
    plt.gca().xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
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
    Process an SLR results file, extract modality data, and generate a bar plot. # noqa:E501

    This script reads a specified SLR (Systematic Literature Review) results file in Excel format, # noqa:E501
    extracts the 'Modality' column from the "ModalityTable" sheet, counts unique modalities, and # noqa:E501
    generates a bar plot of the top 5 most frequent modalities. The plot is then saved to the # noqa:E501
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

    modalityCounts = countModalities(df)
    plotModalities(modalityCounts, outputPath)


if __name__ == "__main__":
    main()
