from business.objects.option import Option
from business.objects.person import Person
import pandas as pd
import numpy as np
from scipy.stats import norm



class BS_formula:

    def __init__(self, option,person,sigma): 
            
        self.s0 = option.S0 # underlying asset price
        self.k = option.K # stike price
        self.r = option.r # risk-free rate
        self.person=person
        self.option=option
        #opt_service=OptionsService()
        #self._sigma = opt_service.calculate_historical_volatility(option,person) # historical return volatility
        self.sigma=sigma
        self.T = option.T # time 2 maturity
        self.d1 = (np.log(self.s0/self.k)+(self.r+self.sigma**2/2)*self.T) / (self.sigma * np.sqrt(self.T))
        self.d2 = ((np.log(self.s0/self.k)+(self.r+self.sigma**2/2)*self.T) / (self.sigma * np.sqrt(self.T))) - self.sigma*np.sqrt(self.T)
        
    def BS_price(self): # calc theoretical price
        c = self.s0*norm.cdf(self.d1) - self.k*np.exp(-self.r*self.T)*norm.cdf(self.d2)
        p = self.k*np.exp(-self.r*self.T)*norm.cdf(-self.d2) - self.s0*norm.cdf(-self.d1)
        
        if self.person.type=='Call':
            return c
        else:
            return p
        
        
    def BS_delta(self): # calc delta
        return norm.cdf(self.d1), norm.cdf(self.d1)-1
    
    def BS_gamma(self): # calc gamma
        return norm.pdf(self.d1)/(self.s0*self._sigma*np.sqrt(self.T)), norm.pdf(self.d1)/(self.s0*self._sigma*np.sqrt(self.T))
    
    def BS_vega(self): # calc vega
        return self.s0*np.sqrt(self.T)*norm.pdf(self.d1), self.s0*np.sqrt(self.T)*norm.pdf(self.d1)
    
    def BS_theta(self): # calc theta 
        c_theta = -self.s0*norm.pdf(self.d1)*self._sigma / (2*np.sqrt(self.T)) - self.r*self.k*np.exp(-self.r*self.T)*norm.cdf(self.d2)
        p_theta = -self.s0*norm.pdf(self.d1)*self._sigma / (2*np.sqrt(self.T)) + self.r*self.k*np.exp(-self.r*self.T)*norm.cdf(-self.d2)
        return c_theta, p_theta
    def BS_rho(self): # calc rho  
        return self.k*self.T*np.exp(-self.r*self.T)*norm.cdf(self.d2), -self.k*self.T*np.exp(-self.r*self.T)*norm.cdf(-self.d2)



if __name__ == "__main__":
    from business.services.opt_service import OptionsService
    
    P=Person('Call')
    for name in ['Apple', 'Amazon', 'Ali baba', 'Google', 'Meta', 'Microsoft', 'Sony', 'Tesla']:
        print(name)
        O=Option(name=name, K=190, T=0.75,r=0.0525 )
        opt_service=OptionsService()
        print("Options Data:")
        opt_service.get_options_data(O,P)
        
        #print("Implied Volatilities:")
        #print(opt_service.get_volatilities(O,P))
        
        print("Volatility:")
        sigma=opt_service.calcul_impl_volatility(O,P)
        print(sigma)

        # Create an instance of the Black-Scholes model
        print("BS Price:")
        bsm = BS_formula( O, P,sigma)

        # Calculate option prices
        call_price = bsm.BS_price()

        print(f"The theoretical price of the call option is: {call_price}")

        print(30 * "-")
        
    
    