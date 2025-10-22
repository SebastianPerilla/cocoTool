import pandas as pd
import numpy as np

class FreightSize:
    def __init__(self, dataframe: pd.DataFrame, lengthCol: str, widthCol: str, heightCol: str, 
                freightRatioInput: float, 
                dutyMultiplierInput: float,
                bqtPriceCol: str, bunchPerBoxCol: str,
                priceKiloInput: float,
                extrasCol: str, boxTotalCol: str,):
        
        self.dataframe = dataframe
        self.lengthCol = lengthCol
        self.widthCol = widthCol
        self.heightCol = heightCol
        self.freightRatioInput = freightRatioInput
        self.dutyMultiplierInput = dutyMultiplierInput
        self.bqtPriceCol = bqtPriceCol
        self.bunchPerBoxCol = bunchPerBoxCol
        self.priceKiloInput = priceKiloInput
        self.extrasCol = extrasCol
        self.boxTotalCol = boxTotalCol
      
      
    def roundedVolumeCalc(self):
        # Volume
        length = self.dataframe[self.lengthCol]
        width = self.dataframe[self.widthCol]
        height = self.dataframe[self.heightCol]
        freightRatio = self.freightRatioInput

        volume = (length * width * height) / freightRatio   # Volume
        
        self.dataframe['ROUNDED_VOLUME'] = np.ceil(volume)  # Rounded Volume
        roundedVolume = self.dataframe['ROUNDED_VOLUME']
        
        return roundedVolume
        
        
    def boxPrice(self):
        # Box Price
        self.dataframe['BOX_PRICE'] = self.roundedVolumeCalc() * self.priceKiloInput
        boxPrice = self.dataframe['BOX_PRICE']
        return boxPrice
            

    def tariffDuties(self):
        # Tariff Duties
        dutyMultiplier = self.dutyMultiplierInput
        priceBQT = self.dataframe[self.bqtPriceCol]
        bunchPerBox = self.dataframe[self.bunchPerBoxCol]
        
        self.dataframe['TARIFF_DUTY'] = (priceBQT * bunchPerBox) * dutyMultiplier
        tariffDuty = self.dataframe['TARIFF_DUTY']
        
        return tariffDuty


    def freight_size(self):
        # Freight calculation
        boxPrice = self.boxPrice()
        extrasBuffer = self.dataframe[self.extrasCol]
        boxTotal = self.dataframe['UNITS'] * self.dataframe['BUNCH_PER_BOX']

        self.dataframe['BQT_FREIGHT_PRICE'] = pd.to_numeric(((boxPrice + extrasBuffer + self.tariffDuties()) / boxTotal)).round(2)
        bqtFreightPrice = self.dataframe['BQT_FREIGHT_PRICE']

        return bqtFreightPrice


class WetPacks:
    def __init__(self, dataframe: pd.DataFrame,
                 wetPackConstantInput: float,
                 wetPackPriceInput: float,
                 cubeConstantInput: float,
                 wetPackTransportPalletPriceInput: float,
                 lengthCol: str,
                 widthCol: str,
                 heightCol: str,
                 bunchPerBoxCol: str,
                 wetPackButton: bool):
        
        self.dataframe = dataframe
        self.wetPackConstantInput = wetPackConstantInput
        self.wetPackPriceInput = wetPackPriceInput
        self.cubeConstantInput = cubeConstantInput
        self.wetPackTransportPalletPriceInput = wetPackTransportPalletPriceInput
        self.lengthCol = lengthCol
        self.widthCol = widthCol
        self.heightCol = heightCol
        self.bunchPerBoxCol = bunchPerBoxCol
        self.wetPackButton = wetPackButton

    def wpDimension(self):
        """Calculate Wet Pack dimensions and cube."""
        wetPackConst = self.wetPackConstantInput
        df = self.dataframe

        # Length, Width, Height adjustments
        df['WP_LENGTH'] = df[self.lengthCol] / wetPackConst
        df['WP_WIDTH'] = df[self.widthCol] / wetPackConst
        df['WP_DEPTH'] = df[self.heightCol] / wetPackConst

        wpHt = df['WP_LENGTH']
        wpWd = df['WP_WIDTH']
        wpDp = df['WP_DEPTH']

        # Cube Calculation
        cubeConst = self.cubeConstantInput
        if self.wetPackButton:
            df['CUBE'] = 2.89  # fixed cube when button is pressed
        else:
            wetPackVolume = (wpHt * wpWd * wpDp)
            df['CUBE'] = pd.to_numeric((wetPackVolume / cubeConst)).round(2)
            
        return df['CUBE']

    def wpBQT(self):
        """Calculate Wet Pack BQT (bunch) price."""
        df = self.dataframe
        wetPackPrice = self.wetPackPriceInput
        transportPallet = self.wetPackTransportPalletPriceInput

        # Pack size
        df['PACK'] = df[self.bunchPerBoxCol]
        wetPackSize = df['PACK']

        # Price per bunch
        df['PRICE_PER_BUNCH'] = pd.to_numeric((wetPackPrice / wetPackSize)).round(2)
        priceBunch = df['PRICE_PER_BUNCH']

        # Final BQT price
        df['WET_PACK_BQT_PRICE'] = priceBunch + transportPallet
        
        return df['WET_PACK_BQT_PRICE']

    def calculate(self):
        """Convenience method to run all calculations."""
        wpCube = self.wpDimension()
        wpBQTPrice = self.wpBQT()
        return wpCube, wpBQTPrice
        


def freight_cost(datafram: pd.DataFrame):
    pass


