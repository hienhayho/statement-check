import sys
import argparse
import polars as pl
from tqdm import tqdm
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from sqlmodel import create_engine, Session, SQLModel, select
from src.settings import setting
from src.utils import read_csv
from src.database.schema import Date, TransactionResult


SQLALCHEMY_DATABASE_URL = setting.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=setting.db_verbose)


def extract_date(row) -> Date:
    date = row[0].split("/")
    return Date(day=int(date[0]), month=int(date[1]), year=int(date[2]))


def convert_to_transaction_result(df: pl.DataFrame):
    data = []
    for row in df.rows():
        date = extract_date(row)
        data.append(
            TransactionResult(
                day=date.day,
                month=date.month,
                year=date.year,
                amount=row[1],
                description=row[2],
                code_id=row[3],
            )
        )
    return data


def insert_to_db(file_path: Path):
    df = read_csv(file_path)
    data = convert_to_transaction_result(df)

    with Session(engine) as session:
        for row in tqdm(data):
            session.add(row)
        session.commit()


def get_db_context(size: int = 5):
    result = []
    with Session(engine) as session:
        stmt = select(TransactionResult).limit(size)
        data = session.exec(stmt)
        for row in data:
            result.append(row)

    table_columns = TransactionResult.__table__.columns.keys()
    context_str = " | ".join(table_columns)
    # Make a context str for llm to understand
    for row in result:
        context_str += "\n"
        context_str += " | ".join([str(getattr(row, col)) for col in table_columns])

    return context_str


def init_db():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database")
    parser.add_argument(
        "--task",
        choices=["insert", "init"],
        default="insert",
    )
    parser.add_argument(
        "--file_path",
        type=str,
        required=False,
    )

    args = parser.parse_args()

    if args.task == "insert":
        insert_to_db(Path(args.file_path))
    elif args.task == "init":
        init_db()
