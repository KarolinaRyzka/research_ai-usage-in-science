import re
from pathlib import Path
from typing import List

import click
import pandas
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.base import RunnableSequence
from langchain_ollama.llms import OllamaLLM
from pandas import DataFrame, Series
from progress.bar import Bar

from src.utils import ifFileExistsExit


def inference(df: DataFrame, model: str = "llama3.1") -> DataFrame:
    data: List[Series] = []

    model: OllamaLLM = OllamaLLM(model=model)
    parser: StrOutputParser = StrOutputParser()

    chain: RunnableSequence = model | parser

    promptTemplate: List[SystemMessage | HumanMessage] = [
        SystemMessage(
            content='Return "True" if tags relate to "Natural Sciences". Else, return "False". Do not return any other text.',  # noqa: E501
        ),
    ]

    with Bar(
        "Checking if paper tags fall under the Natural Science category...",
        max=df.shape[0],
    ) as bar:
        row: Series
        for _, row in df[0:10].iterrows():
            tags: List[str] = row["tags"]
            tags = [x.split("_")[1].strip('"').lower() for x in tags]
            tagString: str = ", ".join(tags)

            promptTemplate.append(HumanMessage(content=tagString))

            resp: str = chain.invoke(input=promptTemplate)

            boolResp: bool = bool(
                re.search(
                    pattern=r"\btrue\b",
                    string=resp,
                    flags=re.IGNORECASE,
                )
            )

            if boolResp:
                data.append(row.to_frame().T)

            bar.next()

        return pandas.concat(objs=data, ignore_index=True)


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
    help="Path to a set of transformed papers",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to store Ollama + OpenAlex transformed papers",
)
def main(inputPath: Path, outputPath: Path) -> None:
    ifFileExistsExit(fps=[outputPath])

    print(f'Reading data from "{inputPath}"...')
    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")

    filteredDF: DataFrame = inference(df=df)

    print(f'Writing data to "{outputPath}"...')
    filteredDF.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
