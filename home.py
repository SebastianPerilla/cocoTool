import streamlit as st
import pandas as pd
import numpy as np
from rowItem import RowItem, SheetNames
from helper import normalize_cols

st.set_page_config(page_title="Heinens", initial_sidebar_state='auto')

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

# ---------- UI header ----------
st.title("Welcome")
st.markdown("#### Choose any products!")

sheetName = homeDataframe.displayOptions(sheetList=homeDataframe.sheetNames())

# Load + normalize
df = RowItem(df="df", dataPath=dataPath, chosenSheet=sheetName).produceDataframe()
df.columns = normalize_cols(df.columns)

# Ensure key numeric columns are numeric
for c in ["COSTO_TOTAL", "BUNCH_X_CAJA", "PRECIO_KILO", "DUTIES", "PRICE_CLIENTE", "TRANSP_/PALL"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ---------- Per-item adders (bilingual, intuitive, real defaults from sheet) ----------
with st.sidebar:
    st.markdown("#### Parámetros de Costo / Cost Parameters (sumas)")
    
    # Constants
with st.sidebar.expander("⚙️ Constantes / Constants (modificables)", expanded=False):
    ratioFleteInp = st.number_input("Divisor Volumen / Volume Divisor (Ratio Flete)", min_value=1.0, value=6000.0, step=10.0)
    dutyMulti = st.number_input("Multiplicador Derechos / Duties Multiplier", min_value=0.0, value=0.218, step=0.001, format="%.3f")
    wetPackConstInp = st.number_input("cm → pulgadas / cm → inches (2.54)", min_value=0.0001, value=2.54, step=0.01)
    cubeConstInp = st.number_input("in³ por ft³ / in³ per ft³ (1728)", min_value=1.0, value=1728.0, step=1.0)
    precioKiloInp = st.number_input("Price per Kilo/ Precio por Kilo", min_value=1.0, value=1.95, step=1.0)
    pricePerCube_const = st.number_input("Precio por Cubo / Price per Cube", min_value=0.0, value=2.18, step=0.01)
    pricePerPiece_const = st.number_input("Precio por Pieza / Price per Piece", min_value=0.0, value=0.50, step=0.01)
    fuelConst = st.number_input("Constante Combustible / Fuel Constant", min_value=0.0, value=0.30, step=0.01)
    
with st.sidebar.expander("Wet Pack (Costo Adicional)",  expanded=False):
    wetPackButton = st.checkbox(label='Añadir Wet Pack (MUST PRESS)')
    wetPackPriceInp = st.number_input("Wet Pack Price", min_value=0.00, value=0.00, step=1.00)
    wetPackTransPal = st.number_input("Transportation Palette", min_value=0.00, value=0.00, step=1.00)
    
    st.markdown("---")

with st.sidebar:
    # ======== NEW: Margin presets (steps of 5%), default 15% ========
    margin_options = list(range(0, 101, 5))
    margin_pct = st.selectbox(label="📈 Margen / Margin (% of price)",
                              options=margin_options,
                              index=margin_options.index(15),  # sets default 15%
                              )
    
    margin = margin_pct / 100.0
    # Convert margin (profit as % of price) -> markup (increase over cost)
    markup = (margin / (1 - margin)) if margin < 1 else 0.0
    st.caption(
        f"Equivalente a aumento sobre costo (markup): **{markup*100:.2f}%** · "
        f"Razón costo/precio (cost/price): **{1 - margin:.4f}**"
    )


# ---------- Main selector (first column is usually PRODUCT) ----------
event = st.dataframe(
    df.iloc[:, 0],
    width="stretch",
    on_select="rerun",
    selection_mode="multi-row",
    key="preview_table",
    hide_index=True,
)

# ---------- Compute final view for selected rows (now shown & downloaded from sidebar) ----------
with st.sidebar:
    st.header("Productos seleccionados/Selected Products")
    products = event.selection.rows
    newDF = df.iloc[products].copy() if products else pd.DataFrame()

    if not newDF.empty:
        if "COSTO_TOTAL" not in newDF.columns:
            st.error(f"No se encontró la columna COSTO_TOTAL. Columnas disponibles: {list(newDF.columns)}")
        else:
            # Base cost shown tod the user
            # Flete Miami
            
            # Volume
            length = df['LENGTH']
            width = df['WIDTH']
            height = df['HEIGHT']
            ratioFlete = ratioFleteInp

            df['VOLUME'] = (length * width * height) / ratioFlete  # Volume
            df['ROUNDED_VOLUME'] = np.ceil(df['VOLUME'])    # Rounded Volume

            roundedVol = df['ROUNDED_VOLUME']

            # Precio Caja
            df['PRECIO_CAJA'] = roundedVol * df['PRECIO_KILO']

            # Duties
            dutyMultiplier = dutyMulti
            precioBQT = df['PRECIO/_BQT']
            bunchCaja = df['BUNCH_X_CAJA']
            df['DUTIES'] = ( precioBQT * bunchCaja) * dutyMultiplier


            #FLETE
            precioKilo = precioKiloInp
            precioCaja = roundedVol * precioKilo
            extrasBuffer = df['EXTRAS']
            duties = df['DUTIES']
            totalCaja = df['TOTAL_CAJA']
            df['FLETE_/BQT'] = pd.to_numeric(((precioCaja + extrasBuffer + duties) / totalCaja)).round(2)
                        
            # WET PACKS

            # HT
            wetPackConst = wetPackConstInp
            df['HT'] = df['LENGTH'] / wetPackConst

            # WD
            df['WD'] = df['WIDTH'] / wetPackConst

            # DP
            df['DP'] = df['HEIGHT'] / wetPackConst

            # CUBE
            cubeConst = cubeConstInp
            ht = df['HT']
            wd = df['WD']
            dp = df['DP']
            
            if wetPackButton:
                df['CUBE'] = 2.89
                # print(df['CUBE'])
            else:
                df['CUBE'] = pd.to_numeric(((ht * wd * dp) / cubeConst)).round(2)
            
            # Price Bunch
            wetPackPrice = wetPackPriceInp
            df['PACK']= df['BUNCH_X_CAJA']
            wetPackSize = df['PACK']
            # print(f"Wetpack Pack", wetPackSize[0])
            # print('Wet Pack Price', wetPackPrice)

            df['PRICE_/BUNCH'] = pd.to_numeric(( wetPackPrice / wetPackSize)).round(2)
            # print("Wet Pack Price/BUCH",df['PRICE_/BUNCH'])
            
            # WP/BQT
            priceBunch = df['PRICE_/BUNCH']
            transportPallet = wetPackTransPal
            # print(f"Transport Pallet",transportPallet)
            df['WP/BQT'] = priceBunch + transportPallet   
            # print("WT/BQT",df['WP/BQT'][0])        

            # Freight
            cube = df['CUBE']
            df['CUBE_WET_PACK'] = cube.round(2)

            # Price Per Piece
            cubeWetPack = pd.to_numeric(df['CUBE_WET_PACK'])
            # print(cubeWetPack[0])
            pricePerCube = pricePerCube_const
            pricePerPiece = pricePerPiece_const
            fuelConst = fuelConst
            df['FUEL'] = ((pricePerCube * pricePerPiece * cubeWetPack) * fuelConst).round(2)

            # Price Per Box
            fuel = df['FUEL']
            # print(f"Fuel", fuel[0])

            df['PRICE_PER_BOX'] = pd.to_numeric((cubeWetPack * (pricePerCube + pricePerPiece + fuel))).round(2)
            
            
            # FEEUU / BQT
            packs = df['PACK']
            pricePerBox = df['PRICE_PER_BOX']
            df['F.EEUU/_BQT'] = pd.to_numeric((pricePerBox / packs)).round(2)
             
            
            costoTotal = df['PRECIO/_BQT'] + df['FLETE_/BQT'] + df['F.EEUU/_BQT'] + df['WP/BQT']
            
            
            newDF["COSTO_TOTAL"] = pd.to_numeric(costoTotal, errors="coerce").round(2)

            # <-- use the sidebar variables (adders) to affect price
           
            # effective cost used only for the calculation; we don't show it
            effective_cost = newDF["COSTO_TOTAL"]

            # price = (effective cost) * (1 + markup)
            newDF["PRICE_CLIENTE"] = (effective_cost * (1 + markup)).round(2)

            # print(newDF['PRICE_CLIENTE'][0])
            # Show ONLY these columns (no costo ajustado)
            display_cols = [c for c in ["PRODUCT", "BUNCH_X_CAJA", "COSTO_TOTAL", "PRICE_CLIENTE"] if c in newDF.columns]
            st.dataframe(newDF[display_cols], width="stretch", hide_index=True)

            # CSV download WITHOUT COSTO_TOTAL
            download_cols = [c for c in display_cols if c != "COSTO_TOTAL"]
            csv_bytes = newDF[download_cols].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Descargar CSV / Download CSV (sin Costo Total)",
                data=csv_bytes,
                file_name="productos_seleccionados.csv",
                mime="text/csv",
            )
    else:
        st.info("Selecciona productos para ver y descargar. / Select products to view and download.")
