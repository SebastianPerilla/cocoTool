import pandas as pd
import numpy as np

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


def freight_size(dataframe: pd.DataFrame,
                 lengthCol: str, 
                 widthCol: str, 
                 heightCol: str, 
                 freightRatioInput: float, 
                 dutyMultiplierInput: float,
                 bqtPriceCol: str,
                 bunchPerBoxCol: str,
                 tariffDutyCol: str,
                 priceKiloInput: float,
                 extrasCol: str,
                 boxTotalCol: str,
                 bqtFreightPriceCol: str):
    # Flete Miami
    
    # freightColumnsDropped = dropColsList
    # dataframe = dataframe.drop(columns=freightColumnsDropped)
    
    # Volume
    length = dataframe[lengthCol]
    width = dataframe[widthCol]
    height = dataframe[heightCol]
    freightRatio = freightRatioInput

    volume = (length * width * height) / freightRatio   # Volume
    dataframe['ROUNDED_VOLUME'] = np.ceil(volume)       # Rounded Volume

    roundedVolume = dataframe['ROUNDED_VOLUME']

    # Precio Caja
    dataframe['BOX_PRICE'] = roundedVolume * dataframe['PRICE_KILO']
    
    boxPrice = dataframe['BOX_PRICE']

    # Duties
    dutyMultiplier = dutyMultiplierInput
    priceBQT = dataframe[bqtPriceCol]
    bunchPerBox = dataframe[bunchPerBoxCol]
    # Add the Duty Column
    dataframe[tariffDutyCol] = (priceBQT * bunchPerBox) * dutyMultiplier
    
    tariffDuty = dataframe[tariffDutyCol]


    #FLETE
    priceKiloInput = priceKiloInput
    boxPrice = roundedVolume * priceKiloInput
    extrasBuffer = dataframe[extrasCol]     # Change this into a streamlit input
    duties = dataframe[tariffDutyCol]
    boxTotal = dataframe[boxTotalCol]
    # Add the BQT FREIGHT PRICE COLUMN
    dataframe[bqtFreightPriceCol] = pd.to_numeric(((boxPrice + extrasBuffer + duties) / boxTotal)).round(2)
        
    bqtFreightPrice = dataframe[bqtFreightPriceCol]    
        
    return roundedVolume, boxPrice, tariffDuty, bqtFreightPrice


def wetpacks(dataframe: pd.DataFrame):
    pass

def freight_cost(datafram: pd.DataFrame):
    pass