import logging
from collections import deque
from .registry import ADAPTERS
from itertools import count

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Simple console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

# Cache pour les chemins trouvés : cache[type_source, type_cible] = (cost, path)
PATH_CACHE = {}
COUNTER = count()

def find_conversion_path(start_type, target_type):
    """
    Trouve le chemin de conversion le moins coûteux.
    On utilise un algorithme de type Dijkstra simplifié avec un min-heap.
    Pour éviter le problème de comparaison de classes, on ajoute un compteur
    comme tiebreaker.
    """
    if start_type == target_type:
        return (0, [start_type])

    if (start_type, target_type) in PATH_CACHE:
        return PATH_CACHE[(start_type, target_type)]

    import heapq
    heap = []
    # On push un tuple : (cost, tiebreaker, path)
    heapq.heappush(heap, (0, next(COUNTER), [start_type]))
    visited = set()

    best_path = None
    best_cost = float('inf')

    while heap:
        cost, _, path = heapq.heappop(heap)
        last_type = path[-1]

        if last_type == target_type:
            best_path = path
            best_cost = cost
            break

        if last_type in visited:
            continue
        visited.add(last_type)

        for (f, t), adapter_info in ADAPTERS.items():
            if f == last_type:
                new_cost = cost + adapter_info['cost']
                if new_cost < best_cost:
                    new_path = path + [t]
                    # Ajout du tiebreaker ici aussi
                    heapq.heappush(heap, (new_cost, next(COUNTER), new_path))

    if best_path is None:
        PATH_CACHE[(start_type, target_type)] = (None, None)
        return (None, None)

    PATH_CACHE[(start_type, target_type)] = (best_cost, best_path)
    return (best_cost, best_path)


def convert(obj, target_type):
    from_type = type(obj)
    if from_type == target_type:
        return obj

    logger.debug(f"Attempting to convert {from_type.__name__} to {target_type.__name__}")
    cost, path = find_conversion_path(from_type, target_type)
    if path is None:
        raise ValueError(f"Aucun chemin de conversion trouvé entre {from_type.__name__} et {target_type.__name__}")

    current_obj = obj
    for i in range(len(path)-1):
        f_type = path[i]
        t_type = path[i+1]
        adapter_info = ADAPTERS.get((f_type, t_type))
        if adapter_info is None:
            raise ValueError(f"Aucun adaptateur direct trouvé pour {f_type.__name__} -> {t_type.__name__}")
        
        adapter_cls = adapter_info['class']
        validation_func = adapter_info['pre_validation']
        adapter = adapter_cls()
        # Validation
        if validation_func is not None:
            validation_func(adapter, current_obj)
        
        logger.debug(f"Using adapter {adapter_cls.__name__} ({f_type.__name__} -> {t_type.__name__})")
        current_obj = adapter.convert(current_obj)
    return current_obj
