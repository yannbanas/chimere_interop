# Registry des adaptateurs

ADAPTERS = {}  # Clé: (from_type, to_type) ; Valeur: (AdapterClass, cost, fidelity, validations)

def register_adapter(from_type, to_type, cost=1, fidelity='high'):
    """
    Enregistre un adaptateur avec métadonnées optionnelles.
    cost: entier indiquant le "coût" de la conversion (1 par défaut)
    fidelity: string décrivant la fidélité ('high', 'medium', 'low')
    """
    def decorator(cls):
        validations = None
        if hasattr(cls, 'validate_input'):
            validations = cls.validate_input
        ADAPTERS[(from_type, to_type)] = {
            'class': cls,
            'cost': cost,
            'fidelity': fidelity,
            'pre_validation': validations
        }
        return cls
    return decorator

def pre_validation(func):
    """
    Décorateur à appliquer dans la classe adaptateur pour définir une méthode de validation.
    On suppose que l’adaptateur a une méthode `validate_input(obj)` par exemple.
    """
    def wrapper(cls):
        # On récupère le dernier enregistrement (de l’adaptateur en cours)
        # Ce décorateur doit être utilisé après @register_adapter, donc l’adaptateur est déjà enregistré.
        # Il faudra donc un mécanisme pour retrouver l'adaptateur en cours. On peut par exemple stocker le dernier adapter enregistré.
        # Pour simplifier, on fera un registre interne temporaire, ou on le fait en deux temps :
        cls._pre_validation = func
        return cls
    return wrapper
