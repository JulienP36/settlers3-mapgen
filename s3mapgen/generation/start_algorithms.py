"""Implemented departure strategies and geography dispatch."""
START_ALGORITHMS = ('auto', 'balanced', 'islands', 'classic', 'fair')

def check_start_algorithm(value):
    if value not in START_ALGORITHMS:
        raise ValueError(f'Algorithme de départ inconnu : {value}')
    return value

def resolve_start_algorithm(value, island_labels=None):
    check_start_algorithm(value)
    if value in ('classic', 'fair'):
        return value
    if island_labels is not None:
        return 'islands'
    if value == 'islands':
        raise ValueError('Le placement Îles nécessite les îles identifiées par la géographie')
    return 'balanced'
