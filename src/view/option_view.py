from InquirerPy import prompt
from view.abstract_view import AbstractView
from business.objects.person import Person
from business.objects.option import Option
from business.services.bs_formula import BS_formula
from business.services.opt_service import OptionsService

class OptionView(AbstractView):
    """Start view."""
    
    def __init__(self,person):
        """Initialize."""
        self.person=person
        self._questions = [
            {
                "type": "list",
                "message": "Quelle option souhaitez-vous pricer? ",
                "name": "option_name",
                "choices": [
                    "Apple",
                    "Amazon",
                    "Ali Baba",
                    "Google",
                    "Meta",
                    "Microsoft",
                    "Sony",
                    "Tesla"
                ]
            },
            {
                "type": "input",
                "message": "Quel est le prix actuel de l'option? ",
                "name": "S0",
                 "validate": lambda val: val.replace('.','',1).isdigit() and float(val) > 0,
            },
            {
                "type": "input",
                "message": "Quel est le strike ? ",
                "name": "K",
                 "validate": lambda val: val.replace('.','',1).isdigit() and float(val) > 0,
            },
            {
                "type": "input",
                "message": "Quel est la date de maturité ? ",
                "name": "T",
                 "validate": lambda val: val.replace('.','',1).isdigit() and float(val) > 0,
            },
            {
                "type": "input",
                "message": "Quel est le taux d'intérêt ? ",
                "name": "r",
                 "validate": lambda val: val.replace('.','',1).isdigit() and float(val) > 0,
            },
            
        ]

    def display(self):
        """Display the view."""
        pass

    def choose(self):
        """Make choice."""
        answers = prompt(self._questions)
        option= Option(name=answers["option_name"],S0=float(answers["S0"]),K=float(answers["K"]),T=float(answers["T"]),r=float(answers["r"]))
        # Create an instance of the Black-Scholes model
        print("BS Price:")
        opt_service=OptionsService()
        sigma=opt_service.calcul_impl_volatility(option,self.person)
        bsm = BS_formula( option, self.person,sigma=sigma)
        

        print("Volatility:")
        print(f"{sigma[0]:.2f}")

        

        # Calculate option prices
        price = bsm.BS_price()
        if self.person.type=="Call":
            print(f"The theoretical price of the call option is: {price[0]}")
        else:
            print(f"The theoretical price of the call option is: {price[1]}")
        self._questions = [
                {
                    "type": "list",
                    "message": "Voulez-vous avoir le delta ? ",
                    "name": "choix",
                    "choices": [
                        "Oui",
                        "Non"
                    ]
                }
            ]
        answers = prompt(self._questions)
        if answers["choix"]=="Oui":
            delta = bsm.BS_delta()
            if self.person.type=="Call":
                print(f"Le delta du call est de: {delta[0]}")
            else:
                print(f"Le delta du put est de: {delta[1]}")
            
        
        self._questions = [
                {
                    "type": "list",
                    "message": "Voulez-vous pricer une autre option? ",
                    "name": "choix",
                    "choices": [
                        "Oui",
                        "Non"
                    ]
                }
            ]
        answers = prompt(self._questions)
        if answers["choix"]=="Oui":
            return OptionView(Person(self.person.type))
        else:
            # QUIT
            pass

    def plot_greeks_S(self, S_min, S_max) :
        answers = prompt(self._questions)
        option= Option(answers["option_name"],float(answers["S0"]),float(answers["K"]),float(answers["T"]),float(answers["r"]))
        bsm = BS_formula(option, self.person)

        def greeks_S(S):

            d1 = (np.log(S / option.K) + (option.r + 0.5 * bsm._sigma**2) * option.T) / (bsm._sigma * np.sqrt(option.T))
            d2 = d1 - bsm._sigma * np.sqrt(option.T)

            # Delta
            delta = norm.cdf(d1)

            # Gamma
            gamma = norm.pdf(d1) / (S * bsm._sigma * np.sqrt(option.T))

            # Vega
            vega = S * norm.pdf(d1) * np.sqrt(option.T)

            # Theta
            theta = -(S * norm.pdf(d1) * bsm._sigma) / (2 * np.sqrt(option.T)) - option.r * option.K * np.exp(-option.r * option.T) * norm.cdf(d2)

            # Rho
            rho = option.K * option.T * np.exp(-option.r * option.T) * norm.cdf(d2)

            return delta, gamma, vega, theta, rho

        underlying_prices = np.linspace(S_min, S_max, 100)

        greeks_values = np.array([greeks_S(price) for price in underlying_prices])

        # Plot des grecques
        plt.figure(figsize=(12, 8))

        labels = ['Delta', 'Gamma', 'Vega', 'Theta', 'Rho']

        for i in range(5):
            plt.subplot(2, 3, i + 1)
            plt.plot(underlying_prices, greeks_values[:, i], label=labels[i])
            plt.title(labels[i])
            plt.xlabel('Prix de l\'actif sous-jacent')
            plt.legend()

        plt.tight_layout()
        plt.show()

    def plot_greeks_K(self, K_min, K_max) :
        answers = prompt(self._questions)
        option= Option(answers["option_name"],float(answers["S0"]),float(answers["K"]),float(answers["T"]),float(answers["r"]))
        bsm = BS_formula(option, self.person)

        def greeks_K(K):

            d1 = (np.log(option.S0 / K) + (option.r + 0.5 * bsm._sigma**2) * option.T) / (bsm._sigma * np.sqrt(option.T))
            d2 = d1 - bsm._sigma * np.sqrt(option.T)

            # Delta
            delta = norm.cdf(d1)

            # Gamma
            gamma = norm.pdf(d1) / (option.S0 * bsm._sigma * np.sqrt(option.T))

            # Vega
            vega = option.S0 * norm.pdf(d1) * np.sqrt(option.T)

            # Theta
            theta = -(option.S0 * norm.pdf(d1) * bsm._sigma) / (2 * np.sqrt(option.T)) - option.r * K * np.exp(-option.r * option.T) * norm.cdf(d2)

            # Rho
            rho = K * option.T * np.exp(-option.r * option.T) * norm.cdf(d2)

            return delta, gamma, vega, theta, rho

        underlying_strikes = np.linspace(K_min, K_max, 100)

        greeks_values = np.array([greeks_K(strike) for strike in underlying_strikes])

        # Plot des grecques
        plt.figure(figsize=(12, 8))

        labels = ['Delta', 'Gamma', 'Vega', 'Theta', 'Rho']

        for i in range(5):
            plt.subplot(2, 3, i + 1)
            plt.plot(underlying_strikes, greeks_values[:, i], label=labels[i])
            plt.title(labels[i])
            plt.xlabel('Strike')
            plt.legend()

        plt.tight_layout()
        plt.show()
