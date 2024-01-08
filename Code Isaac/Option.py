#import requests_html
import datetime
from datetime import datetime, timedelta
# import feedparser
# import io
# import json
import pandas
# import requests
#import requests_html 
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar


class Option :
    """
    Cette classe définit une option avec les paramètres : 
    ticker : le code du sous jacent sous format str
    option_type : 'call' ou 'put'
    strike : un float indiquant le strike de l'option
    maturity : la maturité en nombre d'années 
    
    """
    def __init__(self, ticker : str, option_type: str, strike : float, maturity : float):
        self.ticker = ticker
        self.strike = strike
        self.maturity = maturity
        if option_type == "call" or option_type == "put" :
            self.option_type = option_type
        else : 
            raise Exception("Sorry, the option type can anly be 'call' or 'put'")
        if ticker == "aapl" :
            self.S_0= 182.01
        elif ticker == "amzn":
            self.S_0 = 145.68
        elif ticker == "baba":
            self.S_0 = 73.22
        elif ticker == "googl":
            self.S_0 = 137.65
        elif ticker == "meta":
            self.S_0 = 351.77
        elif ticker == "msft":
            self.S_0 = 368.63
        elif ticker == "sony":
            self.S_0 = 91.60
        elif ticker == "tsla":
            self.S_0 = 238.93
        else:
            raise Exception("Sorry, choose one of 'aapl', 'amzn', 'baba', 'googl', 'meta', 'msft', 'sony', 'tsla'")

    def recup_data(self):
        name = "data/ListAllOptions"+self.ticker+".csv"
        self.data = pd.read_csv(name)

    def clean_data(self):

        self.data['Volume'] = self.data['Volume'].replace('-',0).astype('float')
        self.data['Strike'] = self.data['Strike'].astype('float')
        self.data['Last Price'] = self.data['Last Price'].astype('float')
        self.data['Bid'] = self.data['Bid'].astype('float')
        self.data['Ask'] = self.data['Ask'].astype('float')
        self.data['Maturity'] = pd.to_datetime(self.data['Maturity'], format='%B %d, %Y')
        self.data['index'] = range(0,len(self.data))

        # Keep one of the call or the put regarding which one have more transactions
        index_to_keep = []

        for date in self.data['Maturity']:
            date_data = self.data[self.data['Maturity']==date]
            for strike in date_data['Strike']:
                ds_data = date_data[date_data['Strike']== strike]
                volume = list(ds_data['Volume'])
                index = list(ds_data['index'])
                max_volume = max(volume)
                index_to_keep.append(index[volume.index(max_volume)])
        index_to_keep = np.unique(index_to_keep)

        # Retirer les options non liquides : Nous considérons arbitrairement qu'une 
        # option n'est pas liquide lorsque son volume de transactions est inférieure à la
        # médiane des transactions (qui est généralement de l'ordre de la dizaine)
        volume = self.data['Volume']
        median_volume = np.median(volume)
        self.data = self.data[self.data['Volume']>=median_volume]


if __name__ == "__main__" :
    call_aapl = Option("aapl", "call", 185, 1)
    call_aapl.recup_data()
    call_aapl.clean_data()
    print(call_aapl.data)