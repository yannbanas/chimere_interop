# Registry des adaptateurs

ADAPTERS = {}  # Clé: (from_type, to_type), Valeur: Classe d'adaptateur

def register_adapter(from_type, to_type):
    """Décorateur pour enregistrer un adaptateur de from_type vers to_type."""
    def decorator(cls):
        ADAPTERS[(from_type, to_type)] = cls
        return cls
    return decorator
