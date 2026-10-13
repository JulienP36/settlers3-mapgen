"""Bounded arithmetic expressions evaluated on deterministic noise fields."""
from __future__ import annotations
import ast
from functools import lru_cache
import numpy as np

DEFAULT_FORMULA = '0.7*fbm(4) + 0.3*ridged(9)'
FORMULA_EXAMPLES = (
    DEFAULT_FORMULA,
    'clamp(fbm(4) - 0.3*r, -1, 1)',
    '0.6*fbm(3) + 0.25*sin(3*pi*x)*cos(3*pi*y)',
    'clamp(fbm(4) + 0.2*abs(perlin(7)), -1, 1)',
)
NOISE_FUNCTIONS = frozenset(('value', 'perlin', 'simplex', 'fbm', 'billow',
                           'turbulence', 'ridged', 'worley', 'domain_warp', 'white',
                           'hybrid_fbm', 'heterogeneous_fbm', 'ridged_multifractal',
                           'worley_f1', 'worley_f2', 'worley_f2_minus_f1'))
FUNCTION_ARITY = {'sin': 1, 'cos': 1, 'abs': 1, 'sqrt': 1,
                  'min': 2, 'max': 2, 'clamp': 3, 'smoothstep': 3}
VARIABLES = frozenset(('x', 'y', 'r', 'pi'))


def _literal(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        if abs(node.value) > 1e6 or not np.isfinite(node.value):
            raise ValueError("Constante invalide (nombre fini, valeur absolue ≤ 1000000).")
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _literal(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    raise ValueError('Les paramètres des bruits et exposants doivent être des nombres constants.')


@lru_cache(maxsize=128)
def parse_formula(expression: str):
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError('La formule est vide.')
    if len(expression) > 1024:
        raise ValueError('La formule dépasse 1024 caractères.')
    try:
        root = ast.parse(expression.strip(), mode='eval').body
    except (SyntaxError, RecursionError) as exc:
        raise ValueError('Syntaxe invalide : utilisez des points décimaux et des parenthèses équilibrées.') from exc
    budget = [0, 0]

    def visit(node, depth=0):
        budget[0] += 1
        if budget[0] > 192 or depth > 24:
            raise ValueError('La formule est trop complexe (192 éléments, profondeur 24 maximum).')
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float) or abs(node.value) > 1e6 or not np.isfinite(node.value):
                raise ValueError('Constante invalide (nombre fini, valeur absolue ≤ 1000000).')
        elif isinstance(node, ast.Name):
            if node.id not in VARIABLES:
                raise ValueError(f'Variable inconnue : {node.id}. Variables : x, y, r, pi.')
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            visit(node.operand, depth+1)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            if isinstance(node.op, ast.Pow) and abs(_literal(node.right)) > 8:
                raise ValueError('Exposant constant limité à [-8, 8].')
            visit(node.left, depth+1); visit(node.right, depth+1)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            name = node.func.id
            if name in NOISE_FUNCTIONS:
                budget[1] += 1
                if budget[1] > 6 or len(node.args) > 3:
                    raise ValueError('Maximum 6 appels de bruit ; arguments : fréquence, octaves, décalage seed.')
                args = [_literal(a) for a in node.args]
                if args and not 0.5 <= args[0] <= 32:
                    raise ValueError('Fréquence comprise entre 0.5 et 32.')
                if len(args) > 1 and (args[1] != int(args[1]) or not 1 <= args[1] <= 8):
                    raise ValueError('Octaves entières comprises entre 1 et 8.')
                if len(args) > 2 and (args[2] != int(args[2]) or abs(args[2]) > 999999):
                    raise ValueError('Décalage seed entier compris entre -999999 et 999999.')
            elif name not in FUNCTION_ARITY or len(node.args) != FUNCTION_ARITY[name]:
                raise ValueError(f'Fonction ou nombre d’arguments invalide : {name}.')
            for arg in node.args:
                visit(arg, depth+1)
        else:
            raise ValueError('Seuls nombres, variables, opérations et fonctions documentées sont autorisés.')

    visit(root)
    return root


def normalize_formula(value):
    if not isinstance(value, str):
        raise ValueError('La formule doit être un texte.')
    expression = value.strip()
    parse_formula(expression)
    return expression


def evaluate_formula(expression, x, y, noise):
    """The caller supplies transformed coordinates and a bounded noise provider."""
    root = parse_formula(expression)
    variables = {'x': x*2, 'y': y*2, 'r': np.sqrt((x*2)**2+(y*2)**2), 'pi': np.pi}
    cache = {}

    def evaluate(node):
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            return variables[node.id]
        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            a, b = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Add): return a+b
            if isinstance(node.op, ast.Sub): return a-b
            if isinstance(node.op, ast.Mult): return a*b
            if isinstance(node.op, ast.Div): return np.divide(a,b)
            return np.power(a,b)
        name = node.func.id
        args = [evaluate(a) for a in node.args]
        if name in NOISE_FUNCTIONS:
            key = (name, *args)
            if key not in cache:
                cache[key] = noise(name, args)
            return cache[key]
        if name == 'sin': return np.sin(args[0])
        if name == 'cos': return np.cos(args[0])
        if name == 'abs': return np.abs(args[0])
        if name == 'sqrt': return np.sqrt(args[0])
        if name == 'min': return np.minimum(*args)
        if name == 'max': return np.maximum(*args)
        if name == 'clamp':
            if np.any(np.asarray(args[1]) > args[2]):
                raise ValueError('clamp : minimum supérieur au maximum.')
            return np.clip(*args)
        low, high, value = args
        if np.any(np.asarray(high) <= low):
            raise ValueError('smoothstep : la borne supérieure doit dépasser la borne inférieure.')
        t = np.clip((value-low)/(high-low), 0, 1)
        return t*t*(3-2*t)

    try:
        with np.errstate(divide='raise', invalid='raise', over='raise'):
            field = np.broadcast_to(np.asarray(evaluate(root), dtype=np.float32), x.shape)
            if not np.isfinite(field).all():
                raise ValueError('La formule produit des valeurs non finies.')
    except (FloatingPointError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError('Calcul impossible : division par zéro, racine négative ou dépassement numérique.') from exc
    return np.clip(field, -1, 1).astype(np.float32)
