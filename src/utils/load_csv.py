import polars as pl


def read_csv(file_path: str) -> pl.DataFrame:
    return pl.read_csv(file_path, ignore_errors=True)
