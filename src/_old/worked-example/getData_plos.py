from math import ceil
from pathlib import Path
from string import Template
from typing import List

import click
import pandas
from common import ifFileExistsExit, saveDFToJSON
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get


def getDocuments(year: int = 2016, resultsPerPage: int = 100) -> DataFrame:
    dfs: List[DataFrame] = []

    urlTemplate: Template = Template(
        template=f"https://journals.plos.org/plosone/dynamicSearch?filterArticleTypes=Research%20Article&filterStartDate={year}-01-01&filterEndDate={year}-12-31&resultsPerPage={resultsPerPage}&unformattedQuery=%22Deep%20Learning%22&q=%22Deep%20Learning%22&page=$page"  # noqa: E501
    )

    pageNum: int = 1

    with Bar("Searching for documents...", max=1) as bar:
        while True:
            url: str = urlTemplate.substitute(page=pageNum)

            resp: Response = get(url=url, timeout=60)
            json: dict = resp.json()

            if pageNum == 1:
                totalDocuments: int = json["searchResults"]["numFound"]
                maxPages: int = ceil(totalDocuments / resultsPerPage)

                bar.max = maxPages

            df: DataFrame = DataFrame(data=json["searchResults"]["docs"])
            dfs.append(df)

            if pageNum >= maxPages:
                bar.next()
                break

            else:
                bar.next()

            pageNum += 1

    documents: DataFrame = pandas.concat(objs=dfs, ignore_index=True)
    documents["doi"] = documents["id"].apply(lambda x: f"https://doi.org/{x}")
    return documents


@click.command()
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Path to save PLOS search results (parquet)",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-y",
    "--year",
    "year",
    required=False,
    help="Year to search data",
    type=int,
    default=2016,
    show_default=True,
)
def main(outputPath: Path, year: int = 2016) -> None:
    ifFileExistsExit(fps=[outputPath])

    df: DataFrame = getDocuments(year=year)
    saveDFToJSON(df=df, filename=outputPath)


if __name__ == "__main__":
    main()
