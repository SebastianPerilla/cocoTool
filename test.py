import streamlit as st
import pandas as pd
import numpy as np
from rowItem import RowItem, SheetNames
import re

st.set_page_config(page_title="Heinens", initial_sidebar_state='auto')

# ---------- helpers ----------
def normalize_cols(cols: pd.Index) -> pd.Index:
    """Collapse whitespace/newlines, trim, upper-case, replace spaces with underscores."""
    return (
        cols.astype(str)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.upper()
            .str.replace(" ", "_")
    )

# ---------- data ----------
dataPath = 'HEINENS.xlsx'
homeDataframe = SheetNames(df='df', dataPath=dataPath)

# ---------- UI header ----------
st.title('Bienvenido Carlos')
st.markdown('#### Escoge los productos que tu quieras')

sheetName = homeDataframe.displayOptions(sheetList=homeDataframe.sheetNames())

df = RowItem(df='df', dataPath=dataPath, chosenSheet=sheetName).produceDataframe()
df.columns = normalize_cols(df.columns)  # e.g., "COSTO\n TOTAL" -> "COSTO_TOTAL", "PRICE \nCLIENTE" -> "PRICE_CLIENTE"

## More Data Cleaning and Column Reconstruction
length = df['Length']
width = df['Width']
height = df['Height']
ratioFlete = 6000


df['volume'] = (length * width * height) / ratioFlete

df['Rounded Volume'] = np.ceil(df['volume'])
df['Rounded Volume']

# Fallback: if your data already has a computed price column, keep it numeric/rounded
if "PRICE_CLIENTE" in df.columns:
    df["PRICE_CLIENTE"] = pd.to_numeric(df["PRICE_CLIENTE"], errors="coerce").round(2)

# Main selector (first column is usually PRODUCT)
event = st.dataframe(
    df.iloc[:, 0],
    width='stretch',
    on_select='rerun',
    selection_mode='multi-row',
    key='preview_table',
    hide_index=True
)

# ---------- Sidebar: parameters, calculation, and download ----------
with st.sidebar:
    st.subheader("Productos seleccionados")

    # Selection
    products = event.selection.rows
    newDF = df.iloc[products].copy() if products else pd.DataFrame()

    # ---- Inputs for cost components ----
    st.markdown("### Parámetros de Costo")

    colA, colB = st.columns(2)
    with colA:
        precio_kilo = st.number_input("💰 Precio por Kilo", min_value=0.0, value=0.0, step=0.01)
        duties = st.number_input("🧾 Duties", min_value=0.0, value=0.0, step=0.01)
        wet_pack = st.number_input("💧 Wet Pack Integration", min_value=0.0, value=0.0, step=0.01)
    with colB:
        price_per_cube = st.number_input("📦 Price per Cube", min_value=0.0, value=0.0, step=0.01)
        fuel_usa = st.number_input("⛽ Fuel EEUU", min_value=0.0, value=0.0, step=0.01)

    st.markdown("---")
    # Markup as % increase over cost
    markup_pct = st.slider("📈 Markup (% incremento sobre costo)", min_value=0.0, max_value=100.0, value=17.65, step=0.05)
    markup = markup_pct / 100.0
    margin_ratio = 1 / (1 + markup) if (1 + markup) != 0 else 0  # cost/price equivalent
    st.caption(f"Equivalente a margen (costo/precio): **{margin_ratio:.4f}**")

    # ---- Compute adjusted price for the selection ----
    if not newDF.empty:
        # Ensure COSTO_TOTAL exists (after normalization it should)
        if "COSTO_TOTAL" not in newDF.columns:
            st.error(f"No se encontró la columna COSTO_TOTAL. Columnas disponibles: {list(newDF.columns)}")
        else:
            # numeric cost
            newDF["COSTO_TOTAL"] = pd.to_numeric(newDF["COSTO_TOTAL"], errors="coerce")

            # Adjusted cost = base cost + user inputs (per-item additive model)
            adders = precio_kilo + duties + wet_pack + price_per_cube + fuel_usa
            newDF["COSTO_AJUSTADO"] = (newDF["COSTO_TOTAL"] + adders).round(2)

            # Price with markup
            newDF["PRICE_CLIENTE"] = (newDF["COSTO_AJUSTADO"] * (1 + markup)).round(2)

            # Friendly display
            display_cols = []
            # Include known columns if present
            for c in ["PRODUCT", "BUNCH_X_CAJA", "COSTO_TOTAL", "COSTO_AJUSTADO", "PRICE_CLIENTE"]:
                if c in newDF.columns:
                    display_cols.append(c)

            st.dataframe(newDF[display_cols], width='stretch', hide_index=True)

            # ---- Download ----
            @st.cache_data
            def save_to_excel(dataframe, filename="productos_seleccionados.xlsx"):
                dataframe.to_excel(filename, index=False)
                return filename

            file_path = save_to_excel(newDF[display_cols])

            with open(file_path, "rb") as f:
                if st.download_button(
                    label="Descargar como Excel",
                    data=f,
                    file_name="productos_seleccionados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ):
                    st.success('XLSX Descargado Correctamente')
    else:
        st.info("Selecciona productos de la tabla principal para calcular y descargarlos.")
