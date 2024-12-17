from .registry import ADAPTERS

from .registry import ADAPTERS
from collections import deque

def find_conversion_path(start_type, target_type):
    """
    Trouve un chemin de conversion du start_type vers target_type en utilisant un BFS sur le graphe des adaptateurs.
    Retourne une liste de types [start_type, ..., target_type] ou None si impossible.
    """
    if start_type == target_type:
        return [start_type]

    # Construire le graphe à partir d'ADAPTERS : les nœuds sont les types
    # Arêtes: s'il existe ADAPTERS[(A, B)], alors A -> B.
    visited = set()
    queue = deque([[start_type]])

    while queue:
        path = queue.popleft()
        last_type = path[-1]
        if last_type == target_type:
            return path

        if last_type not in visited:
            visited.add(last_type)
            # Ajouter les successeurs (types cibles depuis last_type)
            successors = [t for (f, t) in ADAPTERS.keys() if f == last_type]
            for succ in successors:
                new_path = path + [succ]
                queue.append(new_path)

    return None

def convert(obj, target_type):
    """
    Convertit l'objet 'obj' en une instance de 'target_type'.
    Peut utiliser un chemin indirect si aucun adaptateur direct n'est trouvé.
    Choisit le premier chemin trouvé (fallback).
    """
    from_type = type(obj)
    if from_type == target_type:
        return obj  # Pas besoin de convertir
    
    path = find_conversion_path(from_type, target_type)
    if path is None:
        raise ValueError(f"Aucun chemin de conversion trouvé entre {from_type.__name__} et {target_type.__name__}")

    # Appliquer la chaîne de conversions
    current_obj = obj
    for i in range(len(path)-1):
        f_type = path[i]
        t_type = path[i+1]
        adapter_cls = ADAPTERS.get((f_type, t_type), None)
        if adapter_cls is None:
            # Theoretically, shouldn't happen since we found the path from this graph
            raise ValueError(f"Aucun adaptateur direct trouvé pour convertir {f_type.__name__} en {t_type.__name__}")
        adapter = adapter_cls()
        current_obj = adapter.convert(current_obj)
    return current_obj
