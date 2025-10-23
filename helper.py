import pandas as pd
import numpy as np


# Regex to Return Predictable Column names
def normalize_cols(cols: pd.Index) -> pd.Index:
    return (
        cols.astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.upper()
            .str.replace(" ", "_")
    )
