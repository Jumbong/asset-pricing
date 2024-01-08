class Option:
    def __init__(self, name, K, T, r=0.05, S0=None):
        self.name = name.upper()
        if S0 is None:
            self.S0 = self.default_price(self.name)
        else:
            self.S0 = S0
        self.K = K        # Option strike price
        self.T = T        # Time to expiration
        self.r = r        # Risk-free interest rate

    def default_price(self, name):
        prices = {
            "APPLE": 182.01,
            "AMAZON": 145.68,
            "ALI BABA": 73.22,
            "GOOGLE": 137.65,
            "META": 351.77,
            "MICROSOFT": 368.63,
            "SONY": 91.60,
            "TESLA": 238.93
        }
        return prices.get(name, 0)  # Retourne 0 si le nom n'est pas trouvé
