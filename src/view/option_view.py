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
