import datetime
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class Swap :
    def __init__(self, direction:str, notional:float, fixedrate:float, maturitydate, 
                valuedate, floatfrequency:int, fixedfrequency:int, discountindex:str): 
                #discountindex = SOFR ou BGCR ou TGCR
        self.direction = direction.lower()
        self.notional = notional
        self.fixedrate = fixedrate
        self.maturitydate =  pd.to_datetime(maturitydate, format= "%d/%m/%Y")
        self.valuedate = pd.to_datetime(valuedate, format= "%d/%m/%Y")
        self.floatfrequency = floatfrequency
        self.fixedfrequency = fixedfrequency
        self.discountindex = discountindex
        if self.direction == 'pay':
            self.fixedmultiplier = -1
        else:
            self.fixedmultiplier = 1

    def PrintSwapDetails(self):

        swapdetails = 'Direction: ' + str(self.direction)+ '\n' + ' fixed rate: ' \
            + str(self.fixedrate) +'\n Date of value: '+ str(self.valuedate)+ '\n Maturity: ' \
            + str(self.maturitydate) + '\n notional: ' + str(self.notional)

        print(swapdetails)

    def recup_data(self):
        NYFedRates = pd.read_excel("Swap/NYFedRates.xlsx")
        NYFedRates = NYFedRates[NYFedRates['Rate Type']== self.discountindex]
        NYFedRates['Effective Date'] = pd.to_datetime(NYFedRates['Effective Date']).dt.strftime("%d/%m/%Y")
        self.HistRates = NYFedRates[["Effective Date", "Rate Type", "Rate (%)"]] #format de date 'MM/DD/YYYY'
        # Taux d'intérêts SOFR estimés sur le site https://www.commloan.com/research/rate-calculator/
        ratecurve = [[1/12, 0.0533], 
                    [3/12, 0.0531],
                    [6/12, 0.0512],
                    [1, 0.0464],
                    [3, 0.0373],
                    [5, 0.0356], 
                    [7, 0.0354],
                    [10, 0.0356],
                    [15, 0.0362],
                    [30, 0.0348]]

        self.ratecurve = pd.DataFrame(ratecurve, columns = ["tenor", "rate"])


if __name__ == "__main__" :
    testSwap = Swap("pay", 100000, 0.05, '14/01/2025', '14/06/2024', 6, 6, 'SOFR')
    testSwap.PrintSwapDetails()
    testSwap.recup_data()
    print(testSwap.HistRates)
    print(testSwap.ratecurve)
