from os import listdir
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup, ResultSet, Tag
from progress.bar import Bar
from pyfs import resolvePath
from requests import Response, get

NATURE_ID_SUFFIX: str = "10.1126_"
NATURE_SUFFIX: str = "https://www.science.org"


def identifyFiles(directory: Path) -> List[Path]:
    data: List[Path] = []

    file: str
    for file in listdir(path=directory):
        foo: Path = Path(directory, file)
        data.append(foo)

    return data


def downloadData(documents: List[dict], storageDirectory: Path) -> None:
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    }
    with Bar("Downloading HTML files...", max=len(documents)) as bar:
        document: dict
        for document in documents:
            filename: str = (
                NATURE_ID_SUFFIX + document["id"].replace("/", "_") + ".html"
            )
            filepath: Path = Path(storageDirectory, filename)
            url: str = NATURE_SUFFIX + document["link"]

            response: Response = get(url=url, headers=headers)

            if response.status_code == 200:
                soup: BeautifulSoup = BeautifulSoup(
                    markup=response.content,
                    features="lxml",
                )
                with open(file=filepath, mode="w") as htmlFile:
                    htmlFile.write(soup.prettify())
                    htmlFile.close()

            else:
                print("\n", url, response.status_code)

            bar.next()


def main() -> None:
    htmlDirectory: Path = Path("../../data/html/science")
    absHTMLDirectory: Path = resolvePath(path=htmlDirectory)

    documentDirectory: Path = Path("../../data/documents/science")
    absDocumentDirectory: Path = resolvePath(path=documentDirectory)

    absDocumentDirectory.mkdir(parents=True, exist_ok=True)

    files: List[Path] = identifyFiles(directory=absHTMLDirectory)

    file: Path
    for file in files:
        docs: List[dict] = []
        soup: BeautifulSoup = BeautifulSoup(
            markup=open(file),
            features="lxml",
        )

        titles: ResultSet = soup.find_all(
            name="a",
            attrs={"class": "text-reset animation-underline"},
        )
        title: Tag
        for title in titles:
            foo: dict = {}
            link: str = title.get(key="href")
            foo["link"] = link
            foo["id"] = link.split(sep="/")[-1]
            docs.append(foo)

        downloadData(documents=docs, storageDirectory=absDocumentDirectory)


if __name__ == "__main__":
    main()
