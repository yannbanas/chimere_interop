# chimere/exceptions.py
"""Module des exceptions personnalisées."""
class ChimereError(Exception):
    """Classe de base pour les exceptions du framework."""
    pass

class ValidationError(ChimereError):
    """Erreur de validation des données."""
    pass

class ConversionError(ChimereError):
    """Erreur lors de la conversion."""
    pass