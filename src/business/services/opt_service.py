from src.business.objects.option import Option
from src.business.objects.person import Person
from src.business.services.bs_formula import BS_formula
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from scipy.interpolate import interp2d
from scipy.optimize import minimize_scalar
from scipy.stats import norm

import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import warnings

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
from mpl_toolkits.mplot3d import Axes3D

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class OptionsService:
    # def get_options_data(self, option,person):
    #     """
    #     Get options data for a given symbol and time period.
    #     """
    #     if option.name=="APPLE":
    #         name="aapl"
    #     elif option.name=="AMAZON":
    #         name="amzn"
    #     elif option.name=="ALI BABA":
    #         name="baba"
    #     elif option.name=="GOOGLE":
    #         name="googl"
    #     elif option.name=="META":
    #         name="meta"
    #     elif option.name=="MICROSOFT":
    #         name="msft"
    #     elif option.name=="SONY":
    #         name="sony"
    #     elif option.name=="TESLA":
    #         name="tsla"
        
    #     df= pd.read_csv(f'src/data/cleaned_ListAllOptions{name}.csv')
    #     df_filtered=df[df['Type']==person.type]
    #     return df
    
    def get_relative_maturity(self,maturities):
        maturities= pd.to_datetime(maturities, format='%Y-%m-%d')

        initial_date = datetime(2023, 12, 8)
        relative_maturities = []
        
        for maturity in maturities:
            temp_maturity = datetime(maturity.year, maturity.month, maturity.day)
            rel_maturity = relativedelta(temp_maturity, initial_date)
            rel_maturity = rel_maturity.years + rel_maturity.months / 12.0 + rel_maturity.days / 365.25
            relative_maturities.append(rel_maturity)    
        return relative_maturities
    
    # def get_volatilities(self,option,person):
    #     df=self.get_options_data(option,person)
        
    #     strikes=df['Strike']
    #     prices=df['Last Price']
    #     volatilities = []

    #     relative_maturities = self.get_relative_maturity(df['Maturity'])
        
    #     types = df['Type']

    #     for i in range(len(strikes)):
    #         option=Option(name=option.name,K=strikes.iloc[i],T=relative_maturities[i],r=option.r)
    #         person=Person(types.iloc[i])
    #         objective_function = lambda sigma: (BS_formula(option,person,sigma).BS_price() - prices.iloc[i])**2
    #         result = minimize_scalar(objective_function)
    #         implied_vol = result.x
    #         volatilities.append(implied_vol)
        
    #     df['implied Volatility']=volatilities
        
    #     chemin_csv = f"clean_ListAllOptions{option.name}.csv"  # '..' signifie le dossier parent


    #     df.to_csv(chemin_csv, index=False)
        
    #     return df

    def calcul_impl_volatility(self,option,person):
        #df=self.get_volatilities(option,person)
        if option.name=="APPLE":
            name="APPLE"
        elif option.name=="AMAZON":
            name="AMAZON"
        elif option.name=="ALI BABA":
            name="ALI BABA"
        elif option.name=="GOOGLE":
            name="GOOGLE"
        elif option.name=="META":
            name="META"
        elif option.name=="MICROSOFT":
            name="MICROSOFT"
        elif option.name=="SONY":
            name="SONY"
        elif option.name=="TESLA":
            name="TESLA"
        df= pd.read_csv(f'src/data/clean_final_ListAllOptions{name}.csv')
        
        strike=option.K
        strikes=df['Strike']
        types=df['Type']
        volatilities=df['implied Volatility']

        relative_maturities = self.get_relative_maturity(df['Maturity'])
         
        if (option.T,option.K,person.type) in zip(relative_maturities,strikes,types):
            small_data = df[relative_maturities==option.T and strikes==option.K]
            volatility = float(small_data["implied Volatility"].iloc[0])
        else :
            interp_func = interp2d(strikes, relative_maturities, volatilities, kind='linear')
            volatility = interp_func(option.K, option.T)
            
        return volatility

    def plot_volatilities(self, option, person):

        df = pd.read_csv(f'src/data/clean_ListAllOptions{option.name}.csv')
        relative_maturities = np.array(self.get_relative_maturity(df['Maturity']))
        strikes= np.array(df['Strike'])
        volatilities= np.array(df['implied Volatility'])
        print(volatilities)

        fig = go.Figure(data=[go.Surface(
            x=strikes,
            y=relative_maturities,
            z=volatilities,
            
            )])
        # modify the axis to correspond to the data range
        # make the relative maturities axis logarithmic
        fig.update_layout(title='Implied Volatility Surface',
                          scene = dict(
                          xaxis_title='Strike',
                          yaxis_title='Relative Maturity',
                          zaxis_title='Implied Volatility',
                          xaxis=dict(range=[-10+min(strikes), max(strikes)+10],),
                          yaxis=dict(range=[-0.2+min(relative_maturities), max(relative_maturities)]+0.2,),
                          zaxis=dict(range=[min(volatilities), max(volatilities)],),),                          
                          autosize=False,
                          width=800, height=800,
                          margin=dict(l=65, r=50, b=65, t=90))
        
        fig.write_html('first_figure.html', auto_open=True)
        
        

if __name__ == "__main__":
    P=Person('Call')
    O=Option('Google', 100, 100, 1)
    opt_service=OptionsService()
    print("Options Data:")
    print("Volatility:")
    print(opt_service.calcul_impl_volatility(O,P))
    opt_service.plot_volatilities(O, P)
    
    