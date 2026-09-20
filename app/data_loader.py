import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "support_tickets.csv"


def load_data():
    df = pd.read_excel(DATA_PATH)

    df["created_at"] = pd.to_datetime(df["created_at"])

    return df