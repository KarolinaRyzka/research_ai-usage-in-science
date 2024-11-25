from pathlib import Path
from typing import List

import click
import pandas
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM


def identifyModel(inputPath: Path, outputPath: Path):
    df = pandas.read_parquet(inputPath)
    model: OllamaLLM = OllamaLLM(model="llama3.1")

    results = []
    max_iterations = 50

    parser: StrOutputParser = StrOutputParser()

    chain = model | parser

    for i, row in enumerate(df.itertuples(index=False)):
        if i >= max_iterations:
            break

        title = getattr(row, "titles", "n/a")
        doi = getattr(row, "doi", "n/a")

        promptTemplate: List = [
            SystemMessage(
                content="""You are a deep learning model identifier for academic papers.
        Your task is to extract the names of pre-trained models from paper titles alone.
        Return only the name of the identified model. If there are more than one, return them as a
        numbered list. If there are none, return 😞 . You keep responses concise without any extra information.
        input: SceneGPT: A Language Model for 3D Scene Understanding
        output: SceneGPT
        input: DiffLoRA: Generating Personalized Low-Rank Adaptation Weights with Diffusion
        output: DiffLoRA
        input: Self-Supervised Learning on MeerKAT Wide-Field Continuum Images
        output: MeerKAT
        input: Utilize Transformers for translating Wikipedia category names
        output: 😞
        input: Building Decision Making Models Through Language Model Regime
        output: 😞
        """  # noqa: E501
            ),
            HumanMessage(content=f"""{title}"""),
        ]
        parser: StrOutputParser = StrOutputParser()

        chain = model | parser
        resp: str = chain.invoke(input=promptTemplate)

        results.append({"doi": doi, "prompt": title, "response": resp})

    resultsDF = pandas.DataFrame(results)

    resultsDF.to_csv(outputPath, index=False)


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
    help="Path to a transformed set of papers",
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
    help="Path to store data in CSV format",
)
def main(inputPath: Path, outputPath: Path) -> None:
    identifyModel(inputPath, outputPath)


if __name__ == "__main__":
    main()
