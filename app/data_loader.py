import pandas as pd
from pathlib import Path
import os

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "support_tickets.xlsx"
)

def load_data():
    df = pd.read_excel(DATA_PATH)

    df["created_at"] = pd.to_datetime(df["created_at"])

    return df