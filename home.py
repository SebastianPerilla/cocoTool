import streamlit as st
import pandas as pd
import numpy as np
from rowItem import RowItem, SheetNames
from helper import normalize_cols
from colProcessing import FreightSize, WetPacks, FreightEEUU

st.set_page_config(page_title="CocoTool", initial_sidebar_state='auto')

# File Upload
uploaded_file = st.file_uploader(label="Upload your Excel/XLSX file", type=["xlsx"])

if uploaded_file is not None:
    # Read directly from uploaded Excel
    st.success("File uploaded successfully!")
    dataPath = uploaded_file
else:
    st.info("Please upload an Excel/XSLX file to continue.")
    st.stop()

# Data
homeDataframe = SheetNames(df="df", dataPath=dataPath)

# Header
st.title("Welcome")
st.markdown("#### Choose any products!")

sheetName = homeDataframe.displayOptions(sheetList=homeDataframe.sheetNames())

# Load + normalize
df = RowItem(df="df", dataPath=dataPath, chosenSheet=sheetName).produceDataframe()
df.columns = normalize_cols(df.columns)

# Custom Parameters
with st.sidebar:
    st.markdown("# Cost Parameters")
    
# Constants
with st.sidebar.expander("⚙️ Constants (Modifiable)", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        ratioFleteInp = st.number_input(
            "Volume Divisor (Ratio Flete)",
            min_value=1.0, value=6000.0, step=10.0
        )
        dutyMultiInp = st.number_input(
            "Duties Multiplier",
            min_value=0.0, value=0.218, step=0.001, format="%.3f"
        )
        wetPackConstInp = st.number_input(
            "cm → inches (2.54)",
            min_value=0.0001, value=2.54, step=0.01
        )
        cubeConstInp = st.number_input(
            "in³ per ft³ (1728)",
            min_value=1.0, value=1728.0, step=1.0
        )

    with col2:
        precioKiloInp = st.number_input(
            "Price per Kilo",
            min_value=1.0, value=1.95, step=1.0
        )
        pricePerCubeConst = st.number_input(
            "Price per Cube",
            min_value=0.0, value=2.18, step=0.01
        )
        pricePerPieceConst = st.number_input(
            "Price per Piece",
            min_value=0.0, value=0.50, step=0.01
        )
        fuelConst = st.number_input(
            "Fuel Constant",
            min_value=0.0, value=0.30, step=0.01
        )
   
with st.sidebar.expander("Wet Pack (Additional Cost)",  expanded=False):
    wetPackButton = st.checkbox(label='Add Wet Pack (MUST PRESS)')
    wetPackPriceInp = st.number_input("Wet Pack Price", min_value=0.00, value=0.00, step=1.00)
    wetPackTransPalInp = st.number_input("Transportation Palette", min_value=0.00, value=0.00, step=1.00)
    
    st.markdown("---")

with st.sidebar:
    # Margin/Markup Calculator
    margin_options = list(range(0, 101, 5))
    margin_pct = st.selectbox(label="📈 Margen / Margin (% of price)",
                              options=margin_options,
                              index=margin_options.index(15),  # sets default 15%
                              )
    
    margin = margin_pct / 100.0
    # Convert margin (profit as % of price) -> markup (increase over cost)
    markup = (margin / (1 - margin)) if margin < 1 else 0.0
    st.caption(
        f"Markup: percent Increase in Cost: **{markup*100:.2f}%** - "
        f"Cost/Price: **{1 - margin:.4f}**"
    )


# Main Selection
event = st.dataframe(
    df.iloc[:, 0],
    width="stretch",
    on_select="rerun",
    selection_mode="multi-row",
    key="preview_table",
    hide_index=True,
)

# Final Sidebar View
with st.sidebar:
    st.header("Selected Products")
    products = event.selection.rows
    newDF = df.iloc[products].copy() if products else pd.DataFrame()

    if not newDF.empty:
        if "PRODUCT" not in newDF.columns:
            st.error(f"Unable to find the PRODUCT Column. Available Columns: {list(newDF.columns)}")
        else:
            # Base cost shown to the user
            freightColumnsDropped = ['BQT_PRICE','FLETE_MIAMI', 'WET_PACK', 'FREIGHT' ,'TOTAL_COST','BOX_TOTAL','BOX_PRICE','TARIFF_DUTY','BQT_FREIGHT_PRICE','PACK','VOLUME','ROUNDED_VOLUME','BQT_FREIGHT_PRICE','TARIFF_DUTY', 'WP_HEIGHT', 'WP_WIDTH', 'WP_DEPTH', 'CUBE', 'PRICE_PER_BUNCH', 'WET_PACK_BQT_PRICE', 'CUBE_WET_PACK', 'FUEL_PRICE', 'PRICE_PER_BOX', 'FREIGHT_PRICE_PER_BQT_USA']
            df = df.drop(columns=freightColumnsDropped)

            df['BQT_PRICE'] = df['FARM_PRICE'] * df['STEM_BUNCH']

            freightSize = FreightSize(dataframe=df,
                            lengthCol='LENGTH',
                            widthCol='WIDTH',
                            heightCol='HEIGHT',
                            freightRatioInput=ratioFleteInp,
                            dutyMultiplierInput=dutyMultiInp,
                            bqtPriceCol='BQT_PRICE',
                            bunchPerBoxCol='BUNCH_PER_BOX',
                            priceKiloInput=precioKiloInp,
                            extrasCol='EXTRAS',
                            boxTotalCol='BOX_TOTAL')

            wetPackCalc = WetPacks(dataframe=df,
                                   wetPackConstantInput=wetPackConstInp,
                                   wetPackPriceInput=wetPackPriceInp,
                                   cubeConstantInput=cubeConstInp,
                                   wetPackTransportPalletPriceInput=wetPackTransPalInp,
                                   lengthCol='LENGTH',
                                   widthCol='WIDTH',
                                   heightCol="HEIGHT",
                                   bunchPerBoxCol='BUNCH_PER_BOX',
                                   wetPackButton=wetPackButton)
            
            
            freightCostEEUU = FreightEEUU(dataframe=df,
                                          wetpacks=wetPackCalc,
                                          pricePerCubeConstantInput=pricePerCubeConst,
                                          pricePerPieceConstantInput=pricePerPieceConst,
                                          fuelConstantInput=fuelConst)
            
             
            # BQT PRICE + FLETE MIAMI + WET PACK + FREIGHT = TOTAL COST
            totalCost = df['BQT_PRICE'] + freightSize.freightSize() + wetPackCalc.wpBQTPrice() + freightCostEEUU.freightCostUSA()
            
            
            newDF["TOTAL_COST"] = pd.to_numeric(totalCost, errors='coerce').round(2)
                       
            # effective cost used only for the calculation; we don't show it
            effective_cost = newDF["TOTAL_COST"]
            
            if wetPackButton:
                st.warning('Notice: Wet Pack option turned on')

            # price = (effective cost) * (1 + markup)
            newDF["CLIENT_PRICE"] = (effective_cost * (1 + markup)).round(2)

            # Show ONLY these columns (no costo ajustado)
            display_cols = [c for c in ["PRODUCT", "BUNCH_PER_BOX", "TOTAL_COST", "CLIENT_PRICE"] if c in newDF.columns]
            st.dataframe(newDF[display_cols], width="stretch", hide_index=True)
            
            # CSV download WITHOUT Total Cost (Clients cant know this shizzles)
            download_cols = [c for c in display_cols if c != "TOTAL_COST"]
            csv_bytes = newDF[download_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV (without Total Cost column included)",
                data=csv_bytes,
                file_name="selected_products.csv",
                mime="text/csv",
            )
    else:
        st.info("Select products to view and download.")
