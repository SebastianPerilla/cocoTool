import streamlit as st
import pandas as pd
import numpy as np
from rowItem import RowItem, SheetNames

st.set_page_config(page_title="Heinens", initial_sidebar_state='auto')


# ---------- File upload ----------
uploaded_file = st.file_uploader("📤 Sube tu archivo Excel / Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read directly from uploaded Excel
    st.success("Archivo cargado correctamente / File uploaded successfully!")
    dataPath = uploaded_file
else:
    st.info("📄 Por favor sube un archivo Excel para continuar / Please upload an Excel file to continue.")
    st.stop()


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

def default_from(df: pd.DataFrame, col: str, fallback: float) -> float:
    """Pick a sensible default from the sheet if available; otherwise fallback."""
    if col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if not s.empty:
            return float(round(s.median(), 2))
    return float(fallback)

# ---------- data ----------
homeDataframe = SheetNames(df="df", dataPath=dataPath)

# ---------- UI header ----------
st.title("Bienvenido Carlos")
st.markdown("#### Escoge los productos que tú quieras")

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
    st.header("Productos seleccionados/Selected Products")
    st.markdown("#### Parámetros de Costo / Cost Parameters (sumas)")
    
    # ---------- CONSTANTS (bilingual, intuitive, with real defaults) ----------
with st.sidebar.expander("⚙️ Constantes / Constants (modificables)", expanded=False):
    ratioFlete = st.number_input("Divisor Volumen / Volume Divisor (Ratio Flete)", min_value=1.0, value=6000.0, step=10.0)
    dutyMultiplier = st.number_input("Multiplicador Derechos / Duties Multiplier", min_value=0.0, value=0.218, step=0.001, format="%.3f")
    wetPackConst = st.number_input("cm → pulgadas / cm → inches (2.54)", min_value=0.0001, value=2.54, step=0.01)
    cubeConst = st.number_input("in³ por ft³ / in³ per ft³ (1728)", min_value=1.0, value=1728.0, step=1.0)
    # pricePerCube_const = st.number_input("Precio por Cubo / Price per Cube", min_value=0.0, value=2.18, step=0.01)
    pricePerPiece_const = st.number_input("Precio por Pieza / Price per Piece", min_value=0.0, value=0.50, step=0.01)
    fuelConst = st.number_input("Constante Combustible / Fuel Constant", min_value=0.0, value=0.30, step=0.01)
    
    
    
    # # Full width
    # wet_pack_add = st.number_input("💧 Integración Wet Pack / Wet Pack Integration (+)",
    #                                min_value=0.0, value=wet_pack_default, step=0.01, format="%.2f")

    st.markdown("---")

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
    products = event.selection.rows
    newDF = df.iloc[products].copy() if products else pd.DataFrame()

    if not newDF.empty:
        if "COSTO_TOTAL" not in newDF.columns:
            st.error(f"No se encontró la columna COSTO_TOTAL. Columnas disponibles: {list(newDF.columns)}")
        else:
            # Base cost shown to the user
            newDF["COSTO_TOTAL"] = pd.to_numeric(newDF["COSTO_TOTAL"], errors="coerce").round(2)

            # <-- use the sidebar variables (adders) to affect price
           
            # effective cost used only for the calculation; we don't show it
            effective_cost = newDF["COSTO_TOTAL"]

            # price = (effective cost) * (1 + markup)
            newDF["PRICE_CLIENTE"] = (effective_cost * (1 + markup)).round(2)

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
