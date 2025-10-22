# cocoTool

Small Streamlit app for my uncle (Coco) to work more efficienyl  with his Excel/XLSX price sheets, product rows, compute freight / wet-pack / duty costs and produce client-ready pricing exports. This is intended to enable him to work smarter and as a result, provide prices to clients. 

## Overview
cocoTool ingests an Excel workbook (sheet selected by the user), finds the header row, normalizes column names, and runs a sequence of cost calculations to produce final client prices. Calculations are separated into classes to keep logic modular and testable.

## Key features
- Upload Excel sheets and select the sheet to process
- Normalize inconsistent header rows and column names
- Calculate:
  - Freight (volume-based)
  - Wet-pack cube and per-bunch prices
  - Tariff / duties
  - Fuel and US freight per bouquet
  - Final client price with selectable margin
- Display results in the UI and export CSV (hides internal total-cost columns)

## Project structure
- home.py — Streamlit app (UI, inputs, export)
- rowItem.py — Sheet enumeration and header/row cleaning logic
- helper.py — utility functions (e.g., normalize_cols)
- colProcessing.py — core calculation classes:
  - FreightSize — volume, box price, tariff duties, per-bqt freight
  - WetPacks — wet-pack cube, price-per-bunch and wet-pack bqt price
  - FreightEEUU — fuel, price-per-box, USA freight per bqt
- function.ipynb — exploratory notebook used during development
- requirements.txt — Python dependencies

## Installation
On Linux (example):
1. Create and activate a virtualenv:
   python3 -m venv .venv
   source .venv/bin/activate
2. Install dependencies:
   pip install -r requirements.txt

## Run (development)
From project root:
streamlit run home.py

## Inputs & configuration
- Upload an Excel file from the UI.
- Sidebar controls expose configurable constants used in calculations:
  - volume divisor / freight ratio
  - duty multiplier
  - price-per-kilo (for box price)
  - wet-pack options (fixed cube or computed)
  - wet-pack price and transport per pallet
  - price-per-cube / per-piece / fuel constants
  - margin / markup to apply to total cost

## Where to change calculation logic
All cost logic is centralized in `colProcessing.py`. Edit or extend the following classes:
- FreightSize — change volume, duty, or freight formulas
- WetPacks — change cube calculation, pack sizing, or wet-pack pricing
- FreightEEUU — change fuel and US freight formulas

Also:
- `helper.normalize_cols` in `helper.py` controls column normalization and collision handling.
- `rowItem.py` controls how the header row is detected and the DataFrame is prepared.

## Notes & known issues
- Excel header detection assumes a row containing a specific header marker; ensure the uploaded sheet contains the expected marker or adjust `rowItem.py`.
- Non-numeric or localized numeric formats (commas, currency symbols) may require cleaning/conversion before calculations.
- Division-by-zero (e.g., PACK or TOTAL columns) should be guarded in data or code.

## Development suggestions
- Add unit tests for `colProcessing` methods (they are pure/predictable given input DataFrames).
- Validate and coerce numeric columns early (use `pd.to_numeric(..., errors='coerce')`).
- Add duplicate-column detection after normalization.

## License
Open — modify as needed for your project.
