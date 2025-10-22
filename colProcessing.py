import pandas as pd
import numpy as np

class FreightSize:
    def __init__(self, dataframe: pd.DataFrame, lengthCol: str, widthCol: str, heightCol: str, 
                freightRatioInput: float, 
                dutyMultiplierInput: float,
                bqtPriceCol: str, bunchPerBoxCol: str,
                priceKiloInput: float,
                extrasCol: str, boxTotalCol: str,):
        
        self.dataframe = dataframe                      # DataFrame Name
        self.lengthCol = lengthCol                      # Length Column Name
        self.widthCol = widthCol                        # Width Column Name
        self.heightCol = heightCol                      # Height Column Name
        self.freightRatioInput = freightRatioInput      # Freight Ratio Input Number
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


    def freightSize(self):
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

    def wpCube(self):
        # Calculate Wet Pack dimensions and cube.
        wetPackConst = self.wetPackConstantInput

        # Length, Width, Height adjustments
        self.dataframe['WP_LENGTH'] = self.dataframe[self.lengthCol] / wetPackConst
        self.dataframe['WP_WIDTH'] = self.dataframe[self.widthCol] / wetPackConst
        self.dataframe['WP_DEPTH'] = self.dataframe[self.heightCol] / wetPackConst

        wpHt = self.dataframe['WP_LENGTH']
        wpWd = self.dataframe['WP_WIDTH']
        wpDp = self.dataframe['WP_DEPTH']

        # Cube Calculation
        cubeConst = self.cubeConstantInput
        if self.wetPackButton:
            self.dataframe['CUBE'] = 2.89  # fixed cube when button is pressed
        else:
            wetPackVolume = (wpHt * wpWd * wpDp)
            self.dataframe['CUBE'] = pd.to_numeric((wetPackVolume / cubeConst)).round(2)
            
        wpCube = self.dataframe['CUBE']
            
        return wpCube

    def wpBQTPrice(self): 
        wetPackPrice = self.wetPackPriceInput
        transportPallet = self.wetPackTransportPalletPriceInput

        # Pack size
        self.dataframe['PACK'] = self.dataframe[self.bunchPerBoxCol]
        wetPackSize = self.dataframe['PACK']

        # Price per bunch
        self.dataframe['PRICE_PER_BUNCH'] = pd.to_numeric((wetPackPrice / wetPackSize)).round(2)
        priceBunch = self.dataframe['PRICE_PER_BUNCH']

        # Final BQT price
        self.dataframe['WET_PACK_BQT_PRICE'] = priceBunch + transportPallet
        wpBQTPrice = self.dataframe['WET_PACK_BQT_PRICE']
        
        return wpBQTPrice        



class FreightEEUU:
    def __init__(self, 
                 dataframe: pd.DataFrame,
                 wetpacks: "WetPacks",
                 pricePerCubeConstantInput,
                 pricePerPieceConstantInput,
                 fuelConstantInput):
        self.dataframe = dataframe
        self.wetpacks = wetpacks
        self.pricePerCubeConstantInput = pricePerCubeConstantInput
        self.pricePerPieceConstantInput = pricePerPieceConstantInput
        self.fuelConstantInput = fuelConstantInput


    # Fuel Price
    def fuelPrice(self):
        wpCube = self.wetpacks.wpCube()         
        pricePerCube = self.pricePerCubeConstantInput
        pricePerPiece = self.pricePerPieceConstantInput
        fuelConst = self.fuelConstantInput
        
        self.dataframe['FUEL'] = ((pricePerCube * pricePerPiece * wpCube) * fuelConst).round(2)
        fuelPrice = self.dataframe['FUEL']
        
        return fuelPrice
        
    # Price Box
    def pricePerBox(self):
        self.dataframe['PRICE_PER_BOX'] = pd.to_numeric((self.wetpacks.wpCube() * (self.pricePerCubeConstantInput + self.pricePerPieceConstantInput + self.fuelPrice()))).round(2)
        pricePerBox = self.dataframe['PRICE_PER_BOX']
    
        return pricePerBox
    
    # Freight USA Cost Per BQT
    def freightCostUSA(self):    
        packs = self.dataframe['BUNCH_PER_BOX']
        self.dataframe['FREIGHT_PRICE_PER_BQT_USA'] = pd.to_numeric((self.pricePerBox() / packs)).round(2)
        
        freightPricePerBQTUSA =  self.dataframe['FREIGHT_PRICE_PER_BQT_USA']
        
        return freightPricePerBQTUSA
