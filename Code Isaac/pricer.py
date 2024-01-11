import Option
from Option import Option
from scipy.interpolate import interp2d
from scipy.optimize import minimize_scalar
from scipy.stats import norm
import pandas as pd
import numpy as np
import datetime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

r_USA = 0.0525 

def black_scholes(S_0, K, T, r, volatility, option_type):
    d1 = (np.log(S_0 / K) + (r + 0.5 * volatility**2) * T) / (volatility * np.sqrt(T))
    d2 = d1 - volatility * np.sqrt(T)

    if option_type == 'call':
        option_price = S_0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        option_price = K * np.exp(-r * T) * norm.cdf(-d2) - S_0 * norm.cdf(-d1)
    else:
        raise ValueError("Type d'option non valide. Utilisez 'call' ou 'put'.")

    return option_price

class Pricer:

    """
    Cette classe permet de pricer une option qui lui est donnée en paramètre. 
    Le second paramètre nécessaire est le taux d'intérêt dont la valeur par défaut est 
    le taux d'intérêt actuel des USA qui vaut 5.25%.

    La classe implémente la méthode de Black-Scholes. Celle ci permet de trouver la volatilité 
    implicite puis de pricer le produit.
    """
    
    def __init__(self, option : Option, r=r_USA):
        option.recup_data()
        option.clean_data()
        self.option = option
        self.r = r

    def data_volatilities(self):
        strikes = self.option.data["Strike"]
        prices = self.option.data['Last Price']
        volatilities = []

        #Récupérer les maturités et en déduire la différence de temps entre cette maturité et la date de
        # récupération des données considéré comme l'instant de pricing (08/12/2023) 
        maturities = list(self.option.data["Maturity"])
        types = list(self.option.data["Type"])
        initial_date = datetime(2023, 12, 8)
        relative_maturities = []
        for maturity in maturities:
            temp_maturity = datetime(maturity.year, maturity.month, maturity.day)
            rel_maturity = relativedelta(temp_maturity, initial_date)
            rel_maturity = rel_maturity.years + rel_maturity.months / 12.0 + rel_maturity.days / 365.25
            relative_maturities.append(rel_maturity)

        for i in range(len(strikes)):
            objective_function = lambda sigma: (black_scholes(self.option.S_0, strikes.iloc[i], 
            relative_maturities[i], self.r, sigma, types[i].lower()) - prices.iloc[i])**2
            result = minimize_scalar(objective_function)
            implied_vol = result.x
            volatilities.append(implied_vol)

        self.option.data["implied Volatility"] = volatilities
        self.option.data["implied Volatility"] = self.option.data["implied Volatility"].astype('float')


    def calcul_impl_volatility(self):
        strike = self.option.strike
        strikes = list(self.option.data["Strike"])
        types = list(self.option.data["Type"])
        volatilities = list(self.option.data["implied Volatility"])

        maturities = list(self.option.data["Maturity"])
        initial_date = datetime(2023, 12, 8)
        relative_maturities = []
        for maturity in maturities:
            temp_maturity = datetime(maturity.year, maturity.month, maturity.day)
            rel_maturity = relativedelta(temp_maturity, initial_date)
            rel_maturity = rel_maturity.years + rel_maturity.months / 12.0 + rel_maturity.days / 365.25
            relative_maturities.append(rel_maturity) 
        relative_maturities = relative_maturities
        if (self.option.maturity, strike, self.option.option_type) in zip(relative_maturities, strikes, types):
            small_data = self.option.data[relative_maturities==self.option.maturity and strikes==strike]
            
            volatility = float(small_data["implied Volatility"].iloc[0])
        else :
            interp_func = interp2d(strikes, relative_maturities, volatilities, kind='linear')
            volatility = interp_func(self.option.strike, self.option.maturity)
        return volatility

    def calcul_price(self):
        self.data_volatilities()
        implied_vol = self.calcul_impl_volatility()
        return black_scholes(self.option.S_0, self.option.strike, self.option.maturity, self.r, implied_vol, self.option.option_type)

if __name__ == "__main__" :
    call_googl = Option("googl", "call", 73, 0.75)
    pricer_googl = Pricer(call_googl)
    pricer_googl.data_volatilities()
    print("les volatilités implicites estimées")
    print(pricer_googl.option.data['implied Volatility'])
    print("___________________________________________________\n Le prix de l'option est:")
    print(pricer_googl.calcul_price())
