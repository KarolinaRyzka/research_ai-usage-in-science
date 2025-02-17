from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MaxNLocator
from pandas import DataFrame


def countTopics(df, column_name, topics):
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


def plotTopicCount(df, outputPath):
    sns.barplot(data=df, x="Topic", y="Count", palette="muted")

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
