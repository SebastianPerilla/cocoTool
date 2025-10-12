import pandas as pd
import streamlit as st

class RowItem:
    def __init__(self, df: str, dataPath:str, chosenSheet):
        self.df = df
        self.dataPath = dataPath
        self.chosenSheet = chosenSheet       
        
    def produceDataframe(self):   
        self.df = pd.read_excel(io=self.dataPath,sheet_name=self.chosenSheet)
        
        # Basic Data Analysis of moving the Column Name
        self.df = self.df.drop(columns=self.df.columns[0])

        # Change the Headers to the 2nd Row of the Dataframe
        header_row_idx = self.df[self.df.iloc[:, 0] == "PRODUCT"].index[0]
        self.df.columns = self.df.iloc[header_row_idx]
        self.df = self.df.drop(range(header_row_idx + 1)).reset_index(drop=True)

        # Capitalize Farm
        self.df['FARM'] = self.df['FARM'].str.upper()
        
        cleanDataframe = self.df
        
        return cleanDataframe
            
class SheetNames:
    def __init__(self, df, dataPath):
        self.df = df
        self.dataPath = dataPath
        
    def sheetNames(self):
        options = pd.ExcelFile(self.dataPath)    
        sheetList = options.sheet_names
        return sheetList 
    
    def displayOptions(self, sheetList):
        options = st.selectbox(label='',
                       options=sheetList,
                       placeholder='Easter, VDay, Valentine, etc.', 
                       width='stretch',
                       label_visibility='collapsed')
        return options
    