from typing import List

from pandas import DataFrame
from requests import Response

from src.classes.search import Search


class OpenAlex(Search):
    def __init__(self) -> None:
        super().__init__()

    def searchByDOI(self, doiURL: str) -> Response:
        url: str = f"https://api.openalex.org/works/{doiURL}"
        return self.search(url=url)

    def getWorkTopics(self, resp: Response) -> DataFrame:
        data: dict[str, List[str]] = {
            "topic": [],
            "subfield": [],
            "field": [],
        }

        json: dict = resp.json()

        topics: List[dict[str, str | dict[str, str]]] = json["topics"]

        topic: dict
        for topic in topics:
            data["topic"].append(topic["display_name"])
            data["subfield"].append(topic["subfield"]["display_name"])
            data["field"].append(topic["field"]["display_name"])

        return DataFrame(data=data)
