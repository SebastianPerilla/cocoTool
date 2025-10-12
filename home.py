import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Heinens", initial_sidebar_state='auto')


dataPath = 'HEINENS.xlsx'
df = pd.ExcelFile(dataPath)

sheetName = df.sheet_names]

easterSheetName = 'EASTER 2026'
df = pd.read_excel(dataPath, sheet_name=0)

# Basic Data Analysis of moving the Column Names
df = df.drop(columns=df.columns[0])

header_row_idx = df[df.iloc[:, 0] == "PRODUCT"].index[0]
df.columns = df.iloc[header_row_idx]
df = df.drop(range(header_row_idx + 1)).reset_index(drop=True)

df['FARM'] = df['FARM'].str.upper()


### Implementation

st.title('Bienvenido Carlos')
st.markdown('#### Escoge los productos que tu quieras')

options = st.selectbox(label='Escoge los tipos de products:',
                       options=sheetName,
                       placeholder='Easter, VDay, Valentine, etc.', 
                       width='stretch')

# st.write('Seleccion', options)
    


preview = df['PRODUCT']

event = st.dataframe(preview, 
             width='stretch', 
             on_select='rerun',
             selection_mode="multi-row",
             hide_index=True)



# === Cacheable function to save selection ===
@st.cache_data
def save_to_excel(dataframe, filename="productos_seleccionados.xlsx"):
    """Save the selected rows to an Excel file and return the file path."""
    dataframe.to_excel(filename, index=False)
    return filename

# === Sidebar ===
with st.sidebar:
    st.subheader("Productos seleccionados")

    products = event.selection.rows
    newDF = df.iloc[products] if products else pd.DataFrame()

    if not newDF.empty:
        select = ['PRODUCT', 'UNIDADES','BUNCH \nX CAJA', 'PRICE \nCLIENTE']
        
        st.dataframe(newDF[select], width='stretch', hide_index=True)

        # Save and cache the file
        file_path = save_to_excel(newDF[select])

        # Download button
        with open(file_path, "rb") as f:
            st.download_button(
                label="Descargar como Excel",
                data=f,
                file_name="productos_seleccionados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Selecciona productos de la tabla principal para descargarlos.")