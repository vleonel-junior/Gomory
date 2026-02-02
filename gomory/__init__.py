"""
Gomory - Package pour la résolution de PLNE par la méthode des coupes de Gomory.

Ce package implémente la méthode des coupes de Gomory pour résoudre des
programmes linéaires en nombres entiers (PLNE).

Caractéristiques:
- Arithmétique exacte avec des fractions (pas de floats)
- Affichage détaillé des tableaux du simplexe
- Traçabilité complète de l'algorithme

Exemple d'utilisation:
    >>> from gomory import Problem, GomorySolver
    >>> 
    >>> # Définir le problème
    >>> problem = Problem(
    ...     objective=[6, 8, 7],
    ...     sense="max",
    ...     constraints=[
    ...         ([4, 6, 8], "<=", 14),
    ...         ([1, 0, 0], "<=", 1),
    ...         ([0, 1, 0], "<=", 1),
    ...         ([0, 0, 1], "<=", 1),
    ...     ],
    ...     integer_vars=[0, 1, 2]
    ... )
    >>> 
    >>> # Résoudre
    >>> solver = GomorySolver(problem, verbose=True)
    >>> result = solver.solve()
    >>> print(result)
"""

__version__ = "1.0.0"
__author__ = "Votre Nom"

# Imports principaux
from .problem import Problem, Constraint, ConstraintType, Sense
from .tableau import Tableau
from .solver import GomorySolver, SolverResult, SolverStatus
from .simplex import SimplexResult, SimplexStatus, primal_simplex, create_initial_tableau
from .dual_simplex import dual_simplex
from .gomory_cut import GomoryCut, generate_gomory_cut, find_cut_row, add_cut_to_tableau
from .display import (
    display_tableau,
    display_solution,
    display_cut,
    display_iteration_summary,
    display_final_result
)
from .fraction_utils import (
    to_fraction,
    floor,
    fractional_part,
    is_integer,
    format_fraction,
    format_fraction_latex,
    to_fraction_list
)

# Liste des exports publics
__all__ = [
    # Classes principales
    "Problem",
    "Constraint",
    "ConstraintType",
    "Sense",
    "Tableau",
    "GomorySolver",
    "SolverResult",
    "SolverStatus",
    "SimplexResult",
    "SimplexStatus",
    "GomoryCut",
    
    # Fonctions de résolution
    "primal_simplex",
    "dual_simplex",
    "create_initial_tableau",
    "generate_gomory_cut",
    "find_cut_row",
    "add_cut_to_tableau",
    
    # Fonctions d'affichage
    "display_tableau",
    "display_solution",
    "display_cut",
    "display_iteration_summary",
    "display_final_result",
    
    # Fonctions utilitaires pour les fractions
    "to_fraction",
    "floor",
    "fractional_part",
    "is_integer",
    "format_fraction",
    "format_fraction_latex",
    "to_fraction_list",
]
