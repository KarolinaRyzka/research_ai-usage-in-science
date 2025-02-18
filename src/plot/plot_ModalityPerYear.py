from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
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
               - 'Modality' (which may contain comma-separated modality names)
               - 'Year Published' (publication year as a string or numeric value) # noqa:E501
    :type df: pandas.DataFrame
    :return: A DataFrame with three columns:
             - 'Year Published': The publication year.
             - 'Modality': The unique modality names.
             - 'Count': The number of occurrences per year.
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


def plotModalitiesPerYear(
    modalityCountsDF: DataFrame, outputPath: Path
) -> None:
    """
    Generate and save a line plot showing the total counts of data modalities over the years. # noqa:E501

    This function takes a DataFrame containing modality counts per year and generates a # noqa:E501
    line plot using Seaborn. Each modality is plotted with a distinct color to visualize trends over time. # noqa:E501

    :param modalityCountsDF: A pandas DataFrame containing at least three columns: # noqa:E501
                             - 'Year Published': The publication year.
                             - 'Modality': The name of the modality.
                             - 'Count': The frequency of the modality in that year. # noqa:E501
    :type modalityCountsDF: pandas.DataFrame
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    stylePath = (
        Path(__file__).resolve().parents[2] / "styles" / "custom.mplstyle"
    )
    plt.style.use(stylePath)
    sns.lineplot(
        data=modalityCountsDF,
        x="Year Published",
        y="Count",
        hue="Modality",
        palette="colorblind",
    )

    plt.title("Total Counts of Data Modalities across the SLR by Year")
    plt.xlabel("Year")
    plt.ylabel("Total Count")
    plt.grid(True, linestyle="--", alpha=1)
    plt.tight_layout()
    plt.savefig(outputPath)


def wrapLabel(label: str, width=20) -> str:
    """
    Wrap a label into multiple lines if it contains more than one word.

    This function splits the label by whitespace and joins the first two words
    with a newline character. If the label contains only one word, it is returned unchanged. # noqa:E501

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
def main(slr: Path, outputPath: Path) -> None:
    """
    Process an SLR results file, extract modality data per year, and generate a line plot. # noqa:E501

    This script reads a specified SLR (Systematic Literature Review) results file in Excel format, # noqa:E501
    extracts the 'Modality' column from the "ModalityTable" sheet, counts unique modalities per year, # noqa:E501
    and generates a line plot showing their distribution over time. The plot is then saved to the # noqa:E501
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
    plotModalitiesPerYear(modalityCounts, outputPath)


if __name__ == "__main__":
    main()
