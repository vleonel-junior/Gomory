"""
Algorithme dual du simplexe.

Ce module implémente l'algorithme dual du simplexe, utilisé après
l'ajout d'une coupe de Gomory quand la solution devient non réalisable.
"""

from fractions import Fraction
from typing import Optional, Callable
from enum import Enum

from .tableau import Tableau
from .simplex import SimplexStatus, SimplexResult


class DualSimplexStatus(Enum):
    """Statut de résolution du simplexe dual."""
    OPTIMAL = "optimal"
    INFEASIBLE = "non réalisable (dual non borné)"
    MAX_ITERATIONS = "nombre maximal d'itérations atteint"


def find_leaving_variable_dual(tableau: Tableau) -> Optional[int]:
    """
    Trouve la variable sortante pour le simplexe dual.
    
    La variable sortante est celle ayant la valeur b_i la plus négative.
    
    Args:
        tableau: Tableau actuel
        
    Returns:
        Indice de la ligne pivot, ou None si réalisable
    """
    min_b = Fraction(0)
    leaving = None
    
    for i in range(tableau.num_rows):
        if tableau.b[i] < min_b:
            min_b = tableau.b[i]
            leaving = i
    
    return leaving


def find_entering_variable_dual(tableau: Tableau, leaving_row: int) -> Optional[int]:
    """
    Trouve la variable entrante pour le simplexe dual.
    
    On calcule le ratio (C_j - Z_j) / a_ij pour a_ij < 0
    et on choisit le minimum (en valeur absolue).
    
    Selon le cours:
    Ratio = (C_j - Z_j) / (Ligne clé)_j avec (Ligne clé)_j < 0
    On choisit le ratio positif minimum.
    
    Args:
        tableau: Tableau actuel
        leaving_row: Indice de la ligne pivot (variable sortante)
        
    Returns:
        Indice de la colonne pivot, ou None si non réalisable
    """
    reduced_costs = tableau.compute_reduced_costs()
    
    min_ratio = None
    entering = None
    
    for j in range(tableau.num_cols):
        aij = tableau.matrix[leaving_row][j]
        
        # On ne considère que les coefficients négatifs
        if aij < 0:
            # Ratio = (C_j - Z_j) / a_ij
            # Comme a_ij < 0, on divise un nombre négatif ou nul par un négatif
            # Le ratio sera positif si (C_j - Z_j) <= 0
            ratio = reduced_costs[j] / aij
            
            # On cherche le ratio positif minimum
            if ratio >= 0:
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
                    entering = j
    
    return entering


def dual_simplex(
    tableau: Tableau,
    max_iterations: int = 1000,
    callback: Optional[Callable[[Tableau, int], None]] = None
) -> SimplexResult:
    """
    Exécute l'algorithme dual du simplexe.
    
    Le dual simplexe est utilisé quand:
    - La solution est optimale pour le dual (coûts réduits <= 0)
    - Mais non réalisable pour le primal (certains b_i < 0)
    
    C'est exactement la situation après l'ajout d'une coupe de Gomory.
    
    Algorithme (selon le cours):
    1. Si tous les b_i >= 0 : optimal, terminer
    2. Sinon, sélectionner la ligne avec b_i minimum (< 0) : ligne pivot
    3. Calculer les ratios (C_j - Z_j) / a_ij pour a_ij < 0
    4. Sélectionner la colonne avec le ratio positif minimum : colonne pivot
    5. Si aucune colonne valide : problème non réalisable
    6. Effectuer le pivot et retourner à l'étape 1
    
    Args:
        tableau: Tableau initial (supposé dual-réalisable)
        max_iterations: Nombre maximal d'itérations
        callback: Fonction appelée après chaque itération
        
    Returns:
        Résultat de l'algorithme
    """
    history = [tableau.copy()]
    current = tableau
    iteration = 0
    
    if callback:
        callback(current, iteration)
    
    while iteration < max_iterations:
        # Vérifier la réalisabilité (optimalité du dual)
        if current.is_feasible():
            z, _ = current.compute_z()
            return SimplexResult(
                status=SimplexStatus.OPTIMAL,
                tableau=current,
                objective_value=z,
                solution=current.get_original_solution(),
                iterations=iteration,
                history=history
            )
        
        # Trouver la variable sortante (ligne avec b_i le plus négatif)
        leaving = find_leaving_variable_dual(current)
        
        if leaving is None:
            # Réalisable (ne devrait pas arriver si is_feasible est correct)
            z, _ = current.compute_z()
            return SimplexResult(
                status=SimplexStatus.OPTIMAL,
                tableau=current,
                objective_value=z,
                solution=current.get_original_solution(),
                iterations=iteration,
                history=history
            )
        
        # Trouver la variable entrante
        entering = find_entering_variable_dual(current, leaving)
        
        if entering is None:
            # Problème non réalisable (dual non borné)
            return SimplexResult(
                status=SimplexStatus.INFEASIBLE,
                tableau=current,
                iterations=iteration,
                history=history
            )
        
        # Effectuer le pivot
        current = current.pivot(leaving, entering)
        iteration += 1
        history.append(current.copy())
        
        if callback:
            callback(current, iteration)
    
    return SimplexResult(
        status=SimplexStatus.MAX_ITERATIONS,
        tableau=current,
        iterations=iteration,
        history=history
    )
