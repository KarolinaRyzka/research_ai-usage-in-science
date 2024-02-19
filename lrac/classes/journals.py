from abc import ABCMeta
from typing import List


class Journal(metaclass=ABCMeta):
    """
    Abstract base class (ABC) to define journal properties.

    This ABC and its respected subclasses are to essentially be non-functional.
    """

    def __init__(self) -> None:
        pass

    @property
    def documentTags(self):
        pass

    @property
    def name(self):
        pass

    @property
    def url(self):
        pass

    @property
    def rssURL(self):
        pass


class Science(Journal):
    name: str = "Science"
    url: str = "https://www.science.org/journal/science"
    rssURL: str = (
        "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science"
    )
    documentTags: List[str] = ["Research Article"]

    def __init__(self) -> None:
        pass


class ScienceSignaling(Journal):
    name: str = "Science Signaling"
    url: str = "https://www.science.org/journal/signaling"
    rssURL: str = (
        "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=signaling"
    )
    documentTags: List[str] = ["Research Article"]

    def __init__(self) -> None:
        pass


class ScienceTranslationalMedicine(Journal):
    name: str = "Science Translational Medicine"
    url: str = "https://www.science.org/journal/stm"
    rssURL: str = "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=stm"
    documentTags: List[str] = ["Research Article"]

    def __init__(self) -> None:
        pass


class ScienceAdvances(Journal):
    name: str = "Science Advances"
    url: str = "https://www.science.org/journal/sciadv"
    rssURL: str = "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciadv"
    documentTags: List[str] = ["Research Article"]

    def __init__(self) -> None:
        pass


class ScienceImmunology(Journal):
    name: str = "Science Immunology"
    url: str = "https://www.science.org/journal/sciimmunol"
    rssURL: str = (
        "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=sciimmunol"
    )
    documentTags: List[str] = ["Research Article"]

    def __init__(self) -> None:
        pass


class ScienceRobotics(Journal):
    name: str = "Science Robotics"
    url: str = "https://www.science.org/journal/scirobotics"
    rssURL: str = (
        "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=scirobotics"
    )
    documentTags: List[str] = ["Research Article"]

    def __init__(self) -> None:
        pass