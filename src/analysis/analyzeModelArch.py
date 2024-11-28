from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series


def countModelArchByYear(df: DataFrame, modelColumn, dateColumn) -> Series:
    df[dateColumn] = pandas.to_datetime(df[dateColumn], errors="coerce")

    # Extract the year from the date column
    df["Year"] = df[dateColumn].dt.year

    # Combine all rows in the model_column, splitting by newline
    expandedRows = (
        df[[modelColumn, "Year"]]
        .dropna()
        .assign(Models=lambda x: x[modelColumn].str.split("\n"))
        .explode("Models")
    )

    # Remove numbering and clean up spaces
    expandedRows["Models"] = (
        expandedRows["Models"].str.split(". ", n=1).str[-1].str.strip()
    )

    # Group by year and count occurrences of each unique model
    model_counts_by_year = (
        expandedRows.groupby(["Year", "Models"])
        .size()
        .reset_index(name="Count")
        .sort_values(by=["Year", "Count"], ascending=[True, False])
    )

    return model_counts_by_year

    getAllArch = "\n".join(df[modelColumn].dropna()).split("\n")
    cleanedData = [model.split(". ", 1)[-1].strip() for model in getAllArch]
    counts = Series(cleanedData).value_counts()

    return counts


def countModelArch(df: DataFrame, modelColumn) -> Series:
    getAllArch = "\n".join(df[modelColumn].dropna()).split("\n")
    cleanedData = [model.split(". ", 1)[-1].strip() for model in getAllArch]
    counts = Series(cleanedData).value_counts()

    return counts


@click.command()
@click.option(
    "-s",
    "--slr",
    "slr",
    help="Path to SLR results",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(slr: Path) -> None:
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="Form1",
        engine="openpyxl",
    )
    df.columns = df.columns.str.strip()
    df = df.rename(
        columns={
            "Do The Author's Use Deep Learning?": "UsesDL",
            "What Is The Method Of PTM Re-Use Per Model?": "ReuseMethod",
            "Open Alex Topic Fields": "Topics",
            "Deep Learning Model(s) Used": "Model Architectures",
        }
    )

    df["Ignore"] = df["Ignore"].astype(bool)

    results = countModelArchByYear(
        df, "Model Architectures", "Paper Publication Date"
    )

    # Print the full DataFrame without truncation
    pandas.set_option("display.max_rows", None)
    print(results)

    # counts = countModelArch(df=keepDF, column="Model Architectures")

    # with pandas.option_context("display.max_rows", None):
    #     print(counts)


if __name__ == "__main__":
    main()
