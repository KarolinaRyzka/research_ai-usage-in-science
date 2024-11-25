from json import loads
from math import ceil
from string import Template
from typing import List

from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame
from progress.bar import Bar
from requests import Response

from src.classes import SEARCH_RESULTS_STOR, SearchResultDataFrameSchema
from src.classes.journalGeneric import Journal_ABC
from src.classes.search import Search
from src.utils import formatText


# unfinished there is no article content no abstract on the pages
class PLOS(Journal_ABC):
    def __init__(self) -> None:
        self.journalName: str = "PLOS"
        self.paperURLTemplate: Template = Template(
            template="https://molcellped.springeropen.com/articles/{paperID}"
        )  # noqa: E501
        # no advance search functionality
        self.searchURLTemplate: Template = Template(
            template="https://journals.plos.org/plosone/dynamicSearch?filterStartDate=${year}-01-01&filterEndDate=${year}-12-31&resultsPerPage=100&q=${query}&sortOrder=DATE_NEWEST_FIRST&page=${page}&filterArticleTypes=Research Article&unfilteredQuery=${query}"  # noqa: E501
        )

    def searchJournal(self, query: str, year: int) -> DataFrame:
        """
        search _summary_

        _extended_summary_

        :param query: _description_
        :type query: str
        :param year: _description_
        :type year: int
        :return: _description_
        :rtype: DataFrame
        """
        data: dict[str, List[str | int | bytes]] = SEARCH_RESULTS_STOR.copy()
        page: int = 1
        maxPage: int = 1

        with Bar(f"Conducting search for {query} in {year}...", max=1) as bar:
            while True:
                if page > maxPage:
                    break

                url: str = self.searchURLTemplate.substitute(
                    query=query,
                    year=year,
                    page=page,
                )

                resp: Response = Search().search(url=url)

                data["year"].append(year)
                data["query"].append(query)
                data["page"].append(page)
                data["url"].append(url)
                data["status_code"].append(resp.status_code)
                data["html"].append(resp.content.decode(errors="ignore"))
                data["journal"].append(self.journalName)

                if page == 1:
                    # Check to ensure that there exists pagination
                    json: dict[str, str] = resp.json()

                    documentsFound: int = json["searchResults"]["numFound"]

                    if documentsFound >= 100:
                        maxPage: int = ceil(documentsFound / 100)
                        bar.max = maxPage
                        bar.update()

                bar.next()
                page += 1

        return SearchResultDataFrameSchema(df=DataFrame(data=data)).df

    def extractPaperURLsFromSearchResult(self, respContent: str) -> List[str]:
        data: List[str] = []

        json: dict = loads(s=respContent)
        searchResults: dict = json["searchResults"]
        docs: List[dict] = searchResults["docs"]

        doc: dict
        for doc in docs:
            (
                data.append(
                    self.paperURLTemplate.substitute(
                        paperID=doc["id"],
                    ),
                )
            )

        return data

    def extractDOIFromPaper(self, url: str) -> str:
        """
        Extracts the DOI from a PLOS article URL.

        This function takes a PLOS article URL and extracts the DOI by splitting
        the URL at the '=' character and returning the second part.

        :param url: The URL of the PLOS article.
        :type url: str
        :return: The extracted DOI from the URL.
        :rtype: str
        """  # noqa: E501
        splitURL: List[str] = url.split(sep="=")
        return splitURL[1]

    def extractTitleFromPaper(self, soup: BeautifulSoup) -> str:
        """
        Extracts the title of a PLOS article from a BeautifulSoup object.

        This function takes a BeautifulSoup object representing a PLOS article's HTML
        content, finds the title element by its tag and attributes, and returns the
        formatted title text.

        :param soup: A BeautifulSoup object containing the parsed HTML of the PLOS article.
        :type soup: BeautifulSoup
        :return: The formatted title of the PLOS article.
        :rtype: str
        """  # noqa: E501
        title: Tag = soup.find(name="h1", attrs={"class": "c-article-title"})
        return formatText(string=title.text)

    def extractAbstractFromPaper(self, soup: BeautifulSoup) -> str:
        """
        Extracts the abstract of a PLOS article from a BeautifulSoup object.

        This function takes a BeautifulSoup object representing a PLOS article's HTML
        content, finds the abstract element by its tag and attributes, and returns the
        formatted abstract text.

        :param soup: A BeautifulSoup object containing the parsed HTML of the PLOS article.
        :type soup: BeautifulSoup
        :return: The formatted abstract of the PLOS article.
        :rtype: str
        """  # noqa: E501
        abstract: Tag = soup.find(
            name="div",
            attrs={"class": "abstract-content"},
        )
        return formatText(string=abstract.text)

    def extractContentFromPaper(self, soup: BeautifulSoup) -> str:
        """
        extractContentFromPaper _summary_

        _extended_summary_

        :param soup: _description_
        :type soup: BeautifulSoup
        :return: _description_
        :rtype: str
        """
        content: Tag = soup.find(
            name="div",
            attrs={"id", "article-container"},
        )

        abstract: Tag = content.find(
            name="div",
            attrs={"class": "abstract-content"},
        )

        references: Tag = content.find(
            name="ol",
            attrs={"class": "reference"},
        )

        if abstract:
            abstract.decompose()

        if references:
            references.decompose()

        return formatText(string=content.text)

    def extractDataSourcesFromPaper(self, soup: BeautifulSoup) -> str:
        data: List[str] = []

        tags: ResultSet = soup.find_all(
            name="div",
            attrs={
                "class": "supplementary-material",
            },
        )

        tag: Tag
        for tag in tags:
            text: str = formatText(string=tag.text)
            data.append(text)

        return " ".join(data)

    def extractJournalTagsFromPaper(self, soup: BeautifulSoup) -> List[str]:
        data: List[str] = []

        tags: ResultSet = soup.find_all(
            name="a",
            attrs={"class": "taxo-term"},
        )

        tag: Tag
        for tag in tags:
            text: str = formatText(string=tag.text)
            data.append(f'"{self.journalName}_{text}"')

        return data
