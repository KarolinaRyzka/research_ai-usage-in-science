from typing import List

import pandas
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get

df: DataFrame = pandas.read_json(
    "data/filter_sampled_searchResponse_plos_08-20-2024.json"
)

df = df[df["ns"] == True]  # noqa: E712

df = df[
    ~df["doi"].isin(
        values=[
            "https://doi.org/10.1371/journal.pone.0146490",
            "https://doi.org/10.1371/journal.pone.0168753",
            "https://doi.org/10.1371/journal.pone.0156505",
        ]
    )
]

with Bar("Filtering data through OpenAlex...", max=df.shape[0]) as bar:
    doi: str
    for doi in df["doi"]:
        url: str = f"https://api.openalex.org/works/{doi}"
        resp: Response = get(url=url, timeout=60)

        json: dict = resp.json()

        citations: List[str] = json["referenced_works"]

        if any(df["doi"].isin(values=citations)):
            print("Hello")

        bar.next()
