from datetime import datetime
from typing import List, Type

from typedframe import TypedDataFrame

RELEVANT_YEARS: List[int] = list(range(2014, datetime.now().year + 1))

SEARCH_QUERIES: List[str] = [
    r'"Deep Learning"',
    r'"Deep Neural Network"',
    r'"Hugging Face"',
    r'"HuggingFace"',
    r'"Model Checkpoint"',
    r'"Model Weights"',
    r'"Pre-Trained Model"',
]

SEARCH_RESULTS_STOR: dict[str, List[str | int | bytes]] = {
    "year": [],
    "query": [],
    "page": [],
    "url": [],
    "status_code": [],
    "html": [],
    "journal": [],
}


class SearchResultDataFrameSchema(TypedDataFrame):
    schema: dict[str, Type] = {
        "year": int,
        "query": str,
        "page": int,
        "url": str,
        "status_code": int,
        "html": str,
        "journal": str,
    }
