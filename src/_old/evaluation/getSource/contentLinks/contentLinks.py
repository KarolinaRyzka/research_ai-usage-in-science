from pathlib import Path
from typing import List
from urllib.parse import urlparse

import click
import pandas
from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame, Series
from progress.bar import Bar


def extractLinks(df: DataFrame) -> DataFrame:
    data: dict[str, List[str]] = {
        "doi": [],
        "link": [],
    }

    with Bar("Extracting links...", max=df.shape[0]) as bar:
        row: Series
        for _, row in df.iterrows():
            soup: BeautifulSoup = BeautifulSoup(
                markup=row["html"], features="lxml"
            )
            articleText: Tag = soup.find(
                "div", class_="article-text", id="artText"
            )

            # Delete irrelevant HTML nodes
            articleInfo: Tag = articleText.find(
                name="div", attrs={"class": "articleinfo"}
            )
            articleInfo.decompose()

            references: Tag = articleText.find(
                name="ol", attrs={"class": "references"}
            )
            references.decompose()

            links: ResultSet[Tag] = articleText.find_all(name="a")

            link: Tag
            for link in links:
                href: str = link.get(key="href")

                if href is None:
                    continue

                if href[0] == "#":
                    continue

                if href.find(row["doi"]) != -1:
                    continue

                data["doi"].append(row["doi"])
                data["link"].append(href)

            bar.next()

    return DataFrame(data=data)


def extractDomains(df: DataFrame) -> DataFrame:
    domains = []
    row: Series
    for _, row in df.iterrows():
        try:
            parsed_url = urlparse(row["link"])
            domain = parsed_url.netloc
            domains.append(domain)
        except Exception as e:
            print(f"Error processing URL {row['link']}: {e}")
            domains.append("N/A")  # In case of an error, append "N/A"
    data: dict[str, List[str]] = {"doi": df["doi"], "link": domains}
    return DataFrame(data=data)


def parseDOIs(df: DataFrame) -> DataFrame:
    df = df[df["status_code"] == 200]
    df["doi"] = df["doi"].apply(lambda x: x.split(".org/")[-1])
    return df[["doi", "html"]]


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a filtered download paper set",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a csv file",
)
def main(inputPath: Path, outputPath: Path) -> None:
    df: DataFrame = pandas.read_parquet(inputPath)
    relevantDF: DataFrame = parseDOIs(df=df)
    linkDF: DataFrame = extractLinks(df=relevantDF).drop_duplicates(
        keep="first", ignore_index=True
    )
    domainDF: DataFrame = extractDomains(linkDF)
    DataFrame.to_csv(domainDF, outputPath)


if __name__ == "__main__":
    main()
