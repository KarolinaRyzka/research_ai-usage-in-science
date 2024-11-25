from pathlib import Path
from typing import List

import click
import pandas
from common import ifFileExistsExit, saveDFToJSON
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get

FIELD_FILTER: set[str] = {
    "Agricultural and Biological Sciences",
    "Environmental Science",
    "Biochemistry Genetics and Molecular Biology",
    "Immunology and Microbiology",
    "Neuroscience",
    "Earth and Planetary Sciences",
    "Physics and Astronomy",
    "Chemistry",
    "Materials Science",
}


def filterWithOpenAlex(df: DataFrame) -> DataFrame:
    data: dict[str, List[str | bool | List[str]]] = {
        "doi": [],
        "field": [],
        "ns": [],
    }

    with Bar("Filtering data through OpenAlex...", max=df.shape[0]) as bar:
        doi: str
        for doi in df["doi"]:
            url: str = f"https://api.openalex.org/works/{doi}"
            resp: Response = get(url=url, timeout=60)

            json: dict = resp.json()

            if json["cited_by_count"] == 0:
                bar.next()
                continue

            fields: List[str] = [
                topic["field"]["display_name"] for topic in json["topics"]
            ]

            data["doi"].append(doi)
            data["field"].append(fields)
            data["ns"].append(
                (
                    True
                    if sum([x in FIELD_FILTER for x in fields]) > 1
                    else False
                ),
            )

            bar.next()

    return DataFrame(data=data)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    required=True,
    help="Path to PLOS search results",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Path to store filtered sampled data",
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
def main(
    inputPath: Path,
    outputPath: Path,
) -> None:
    df: DataFrame
    ifFileExistsExit(fps=[outputPath])

    df: DataFrame = pandas.read_json(path_or_buf=inputPath)

    filteredDF: DataFrame = filterWithOpenAlex(df=df)

    saveDFToJSON(df=filteredDF, filename=outputPath)


if __name__ == "__main__":
    main()
