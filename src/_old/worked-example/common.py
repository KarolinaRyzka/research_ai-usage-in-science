from os.path import isfile
from pathlib import Path
from typing import List

from pandas import DataFrame


def saveDFToJSON(df: DataFrame, filename: str) -> None:
    df.to_json(path_or_buf=filename, index=False, indent=4)


def ifFileExistsExit(fps: List[Path]) -> None:
    fp: Path
    for fp in fps:
        if isfile(path=fp):
            print(f'"{fp}" exists')
            exit(1)
