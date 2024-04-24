from pyfs import resolvePath
from pathlib import Path
from pandas import DataFrame
import pandas
import click
import sqlalchemy
from sqlalchemy import Engine, Connection
from typing import List
from progress.bar import Bar
from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables.base import RunnableSequence
from lrac.createZettels import NATURE_BUCKETS

SYSTEM_PROMPT: str = (
    f'Classify the text as one of the following: {", ".join(NATURE_BUCKETS)}. Format the classification as lowercase. Return in the following JSON schema where xxx is your classification: "category": xxx.'
)


def readDB(dbPath: Path) -> DataFrame:
    dbEngine: Engine = sqlalchemy.create_engine(url=f"sqlite:///{dbPath.__str__()}")
    con: Connection = dbEngine.connect()
    zettels: DataFrame = pandas.read_sql_table(
        table_name="zettels_content",
        con=con,
        index_col="docid",
    )
    con.close()
    return zettels


def inference(model: str, prompt: str) -> str:
    outputParser: JsonOutputParser = JsonOutputParser()
    chatPrompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("user", "{input}"),
        ]
    )

    llm: Ollama = Ollama(model=model)

    chain: RunnableSequence = chatPrompt | llm | outputParser

    print(chain.invoke(input={"input": prompt}))


@click.command()
@click.option(
    "-i",
    "--input",
    "inputDB",
    type=Path,
    required=True,
    help="Path to ZettelGiest DB",
)
@click.option(
    "-m",
    "--model",
    "model",
    type=str,
    required=False,
    default="gemma",
    help="Model to perform inference with. NOTE: Must be accessible via Ollama",
)
def main(inputDB: Path, model: str) -> None:
    dbPath: Path = resolvePath(path=inputDB)
    dbPathDir: Path = dbPath.parent

    df: DataFrame = readDB(dbPath=dbPath)
    relevantDF: DataFrame = df[["c0title", "c8note", "c13filename"]]

    data: List[str] = [" ".join(i) for i in zip(df["c0title"], df["c8note"])]

    with Bar("Classifying data based on title and abstract...", max=len(data)) as bar:
        datum: str
        for datum in data:
            inference(model=model, prompt=datum)
            quit()
            bar.next()


if __name__ == "__main__":
    main()
