from src.business.objects.option import Option
from src.business.objects.person import Person
import pandas as pd
import numpy as np
from scipy.stats import norm



class AsianMCPricer:

    def __init__(self, option: Option,person: Person,sigma: float, n_simulations:int, fen=20): 
            
        self.s0 = option.S0 # underlying asset price
        self.k = option.K # stike price
        self.r = option.r # risk-free rate
        self.person=person
        self.option=option
        self.sigma=sigma
        self.T = option.T # time 2 maturity
        self.fen = fen
        self.n_simulations = n_simulations
        
    def MC_price(self, S, sigma): # calc theoretical price

        dt = self.T / 252  # 252 jours ouvrés dans l'année
    
        call_prices = []
        put_prices = []

        for _ in range(self.n_simulations):
            prices = [S]
            
            for i in range(1, 253):
                dW = np.random.normal()
                price_t = prices[-1] * np.exp((self.r - 0.5 * sigma**2) * dt + sigma * dW * np.sqrt(dt))
                prices.append(price_t)
            
            average_price = np.mean(prices[-self.fen:])
            c_payoff = max(average_price - self.k, 0)
            call_prices.append(np.exp(-self.r * self.T)*c_payoff)
            p_payoff = max(-(average_price - self.k), 0)
            put_prices.append(np.exp(-self.r * self.T)*p_payoff)

        c = np.mean(call_prices)
        p = np.mean(put_prices)
        
        if self.person.type=='Call':
            return c
        else:
            return p
        
        
    def MC_delta(self, epsilon): 
        """
        Calcul du delta par la méthode des différences finies
        epsilon: incrément infinitésimal à considérer
        """
        return (self.MC_price(self.s0+epsilon, self.sigma)-self.MC_price(self.s0, self.sigma))/epsilon
        
        
    
    def MC_gamma(self, epsilon): 
        """
        Calcul du gamma par la méthode des différences finies
        epsilon: incrément infinitésimal à considérer
        """

        
        return (self.MC_price(self.s0+epsilon, self.sigma)+self.MC_price(self.s0-epsilon, self.sigma)-2*self.MC_price(self.s0, self.sigma))/epsilon**2
    
    def MC_vega(self): # calc vega
        return (self.MC_price(self.s0, self.sigma+epsilon)-self.MC_price(self.s0, self.sigma))/epsilon
        

if __name__ == "__main__":
    from src.business.services.opt_service import OptionsService
    
    P=Person('Put')
    for name in ['Apple', 'Amazon', 'Ali baba', 'Google', 'Meta', 'Microsoft', 'Sony', 'Tesla']:
        print(name)
        O=Option(name=name, K=180, T=1,r=0.052 )
        opt_service=OptionsService()
        
        #print("Implied Volatilities:")
        #print(opt_service.get_volatilities(O,P))
        
        print("Volatility:")
        sigma=opt_service.calcul_hist_volatility(O,P)
        print(f"{sigma:.2f}")

        # Create an instance of the Black-Scholes model
        print("MC Price:")
        MCPricer = AsianMCPricer(O, P, sigma, 5000)

        # Calculate option prices
        call_price = MCPricer.MC_price(O.default_price(name), sigma)

        print(f"The theoretical price of the option is: {call_price:.2f}")

        print(30 * "-")
        
        delta = MCPricer.MC_delta(0.001)
        print(f"The delta of the option is: {delta:.2f}")
        break
        