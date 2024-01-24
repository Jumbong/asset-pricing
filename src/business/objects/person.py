class Person:
    """ 
    Objet renfermant des informations supplémentaires sur l'option.
    type (str): Call ou Put ou Straddle
    category (str): Européenne ou Asiatique
    """
    def __init__(self, type:str):
        self.type = type
