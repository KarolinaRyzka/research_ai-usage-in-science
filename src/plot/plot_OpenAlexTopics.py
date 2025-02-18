from pathlib import Path
from typing import List

import click
import matplotlib.pyplot as plt
import pandas
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from pandas import DataFrame


def countTopics(df: DataFrame, column_name: str, topics: List) -> DataFrame:
    """
    Count occurrences of specific topics in a given column of a DataFrame.

    This function iterates through the specified column in the DataFrame and counts # noqa:E501
    how many times each topic appears. The result is returned as a DataFrame with # noqa:E501
    two columns: 'Topic' and 'Count'.

    :param df: A pandas DataFrame containing textual data.
    :type df: pandas.DataFrame
    :param column_name: The name of the column in which to search for topics.
    :type column_name: str
    :param topics: A list of topics to count occurrences for.
    :type topics: List[str]
    :return: A DataFrame with two columns:
             - 'Topic': The unique topic names.
             - 'Count': The number of occurrences of each topic.
    :rtype: pandas.DataFrame
    """
    # Initialize a dictionary to store counts for each topic
    topic_counts = {topic: 0 for topic in topics}

    # Iterate through the column and count occurrences of each topic
    for cell in df[column_name]:
        if pd.notna(cell):  # Check if the cell is not empty
            for topic in topics:
                if topic in cell:
                    topic_counts[topic] += 1

    # Convert the counts to a DataFrame for better visualization
    result_df = pd.DataFrame(
        list(topic_counts.items()), columns=["Topic", "Count"]
    )

    return result_df


def plotTopicCount(df: DataFrame, outputPath: Path) -> None:
    """
    Generate and save a bar plot showing the total count of OpenAlex topic fields identified in an SLR. # noqa:E501

    This function takes a DataFrame containing topic counts, creates a bar plot using Seaborn, # noqa:E501
    and labels each bar with its corresponding count. The x-axis labels are formatted with # noqa:E501
    title case for readability.

    :param df: A pandas DataFrame containing at least two columns:
               - 'Topic': The name of the OpenAlex topic field.
               - 'Count': The frequency of the topic in the dataset.
    :type df: pandas.DataFrame
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    stylePath = (
        Path(__file__).resolve().parents[2] / "styles" / "custom.mplstyle"
    )
    plt.style.use(stylePath)
    sns.barplot(data=df, x="Topic", y="Count", palette="colorblind")

    for index, row in df.iterrows():
        plt.text(
            x=index,
            y=row["Count"] + 0.1,
            s=row["Count"],
            ha="center",
            fontsize=10,
        )

    plt.title(
        "Total Count of Open Alex Topic Fields identied for Papers in SLR",
        fontsize=16,
    )
    plt.xlabel("Open Alex Topic Field", fontsize=12)
    plt.ylabel("Total Count", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    ax = plt.gca()
    ax.set_xticklabels([label.title() for label in df["Topic"]])
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
    Process an SLR dataset, count occurrences of OpenAlex topic fields, and generate a bar plot. # noqa:E501

    This function reads an Excel file containing OpenAlex topic fields, counts the occurrences # noqa:E501
    of predefined topics, and visualizes the results using a bar plot.

    :param slr: The file path to the SLR dataset in Excel format.
                The file must contain a sheet named 'Form1' with a column listing OpenAlex topics. # noqa:E501
    :type slr: Path
    :param outputPath: The file path where the generated figure will be saved.
    :type outputPath: Path
    :return: None. The function processes the data and saves the plot without returning any value. # noqa:E501
    :rtype: None
    """
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="Form1",
        engine="openpyxl",
    )

    column_name = "Open Alex Topic Fields\n"
    topics = [
        "Earth and Planetary Sciences",
        "Physics and Astronomy",
        "Agricultural and Biological Sciences",
        "Environmental Science",
        "Biochemistry, Genetics and Molecular Biology",
        "Chemistry",
        "Immunology and Microbiology",
        "Neuroscience",
    ]
    result = countTopics(df, column_name, topics)
    plotTopicCount(result, outputPath)


if __name__ == "__main__":
    main()
