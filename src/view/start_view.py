from InquirerPy import prompt
from view.abstract_view import AbstractView
from business.objects.person import Person
from view.option_view import OptionView

class StartView(AbstractView):
    """Start view."""
    
    def __init__(self):
        """Initialize."""
        self._questions = [
            {
                "type": "list",
                "message": "Que voulez-vous pricer? ",
                "name": "type_pricer",
                "choices": [
                    "Put",
                    "Call"
                    ]
            }
        ]

    def display(self):
        """Display the view."""
        pass

    def choose(self):
        """Make choice."""
        print("Bonjour, bienvenue dans le pricer d'options.")
        answers = prompt(self._questions)
        return OptionView(Person(answers["type_pricer"]))
