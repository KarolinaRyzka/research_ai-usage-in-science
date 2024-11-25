from typing import List

from pandas import DataFrame
from requests import Response

from src.classes.search import Search


class OpenAlex(Search):
    def __init__(self, email: str | None = None) -> None:
        if email is None:
            super().__init__()
        else:
            super().__init__(
                headers={"User-Agent": f"mailto:{email}"},
            )

        self.topicTracker: dict[str, List[str]] = {
            "topic": [],
            "subfield": [],
            "field": [],
        }

    def searchByDOI(self, doiURL: str) -> Response | None:
        url: str = f"https://api.openalex.org/works/{doiURL}"
        return self.search(url=url)

    def getWorkPrimaryTopic(self, json: dict) -> DataFrame | None:
        data: dict[str, List[str]] = self.topicTracker.copy()

        try:
            json = json["primary_topic"]
            data["topic"].append(json["display_name"])
            data["subfield"].append(json["subfield"]["display_name"])
            data["field"].append(json["field"]["display_name"])
        except TypeError:
            return None

        return DataFrame(data=data)

    def getWorkTopics(self, json: dict) -> DataFrame:
        data: dict[str, List[str]] = self.topicTracker.copy()

        topics: List[dict[str, str | dict[str, str]]] = json["topics"]

        topic: dict
        for topic in topics:
            data["topic"].append(topic["display_name"])
            data["subfield"].append(topic["subfield"]["display_name"])
            data["field"].append(topic["field"]["display_name"])

        return DataFrame(data=data)

    def getCitedByCount(self, json: dict) -> int:
        return int(json["cited_by_count"])
