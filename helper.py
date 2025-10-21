import pandas as pd

def normalize_cols(cols: pd.Index) -> pd.Index:
    """Collapse whitespace/newlines, trim, upper-case, replace spaces with underscores."""
    return (
        cols.astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.upper()
            .str.replace(" ", "_")
    )

def default_from(df: pd.DataFrame, col: str, fallback: float) -> float:
    """Pick a sensible default from the sheet if available; otherwise fallback."""
    if col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if not s.empty:
            return float(round(s.median(), 2))
    return float(fallback)


def freight_size(dataframe: pd.DataFrame):
    pass

def wetpacks(dataframe: pd.DataFrame):
    pass

def freight_cost(datafram: pd.DataFrame):
    pass