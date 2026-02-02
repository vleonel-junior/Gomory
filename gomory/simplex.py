"""
Algorithme du simplexe primal.

Ce module implémente l'algorithme du simplexe pour résoudre
des problèmes de programmation linéaire (maximisation).
"""

from fractions import Fraction
from typing import Optional, Tuple, List, Callable
from enum import Enum

from .tableau import Tableau
from .problem import Problem, ConstraintType


class SimplexStatus(Enum):
    """Statut de résolution du simplexe."""
    OPTIMAL = "optimal"
    UNBOUNDED = "non borné"
    INFEASIBLE = "non réalisable"
    MAX_ITERATIONS = "nombre maximal d'itérations atteint"


class SimplexResult:
    """
    Résultat de l'algorithme du simplexe.
    
    Attributes:
        status: Statut de la résolution
        tableau: Tableau final
        objective_value: Valeur optimale de la fonction objectif
        solution: Solution optimale
        iterations: Nombre d'itérations effectuées
        history: Historique des tableaux (si demandé)
    """
    
    def __init__(
        self,
        status: SimplexStatus,
        tableau: Optional[Tableau] = None,
        objective_value: Optional[Fraction] = None,
        solution: Optional[List[Fraction]] = None,
        iterations: int = 0,
        history: Optional[List[Tableau]] = None
    ):
        self.status = status
        self.tableau = tableau
        self.objective_value = objective_value
        self.solution = solution
        self.iterations = iterations
        self.history = history if history else []
    
    def __str__(self) -> str:
        lines = [f"Statut: {self.status.value}"]
        if self.objective_value is not None:
            lines.append(f"z* = {self.objective_value}")
        if self.solution is not None:
            lines.append(f"Solution: {self.solution}")
        lines.append(f"Itérations: {self.iterations}")
        return "\n".join(lines)


def create_initial_tableau(problem: Problem) -> Tableau:
    """
    Crée le tableau initial du simplexe à partir d'un problème.
    
    Convertit le problème en forme standard en ajoutant des variables d'écart.
    
    Args:
        problem: Problème de programmation linéaire
        
    Returns:
        Tableau initial du simplexe
    """
    n = problem.num_variables
    m = problem.num_constraints
    
    # Compter les variables d'écart nécessaires
    num_slack = sum(1 for c in problem.constraints 
                    if c.constraint_type in [ConstraintType.LEQ, ConstraintType.GEQ])
    
    # Taille totale
    total_vars = n + num_slack
    
    # Construire la matrice
    matrix = []
    b = []
    basis = []
    var_names = list(problem.var_names)
    
    slack_idx = n  # Index de la prochaine variable d'écart
    
    for i, constraint in enumerate(problem.constraints):
        row = list(constraint.coefficients)
        
        # Étendre la ligne pour les variables d'écart
        row.extend([Fraction(0)] * num_slack)
        
        if constraint.constraint_type == ConstraintType.LEQ:
            # Ajouter +1 pour la variable d'écart
            row[slack_idx] = Fraction(1)
            basis.append(slack_idx)
            var_names.append(f"x{slack_idx + 1}")
            slack_idx += 1
        elif constraint.constraint_type == ConstraintType.GEQ:
            # Ajouter -1 pour la variable d'écart (surplus)
            row[slack_idx] = Fraction(-1)
            basis.append(slack_idx)
            var_names.append(f"x{slack_idx + 1}")
            slack_idx += 1
        else:  # EQ
            # Pas de variable d'écart, besoin d'une variable artificielle
            # Pour simplifier, on utilise la méthode des deux phases
            # ou on suppose que le problème est sous forme standard
            raise NotImplementedError("Les contraintes d'égalité nécessitent la méthode des deux phases")
        
        matrix.append(row)
        b.append(constraint.rhs)
    
    # Coefficients de la fonction objectif (variables d'écart ont un coût de 0)
    c = list(problem.objective)
    c.extend([Fraction(0)] * num_slack)
    
    return Tableau(
        matrix=matrix,
        b=b,
        c=c,
        basis=basis,
        var_names=var_names,
        num_original_vars=n
    )


def find_entering_variable(tableau: Tableau) -> Optional[int]:
    """
    Trouve la variable entrante selon la règle de Dantzig.
    
    Pour la maximisation, on choisit la variable avec le plus grand coût réduit positif.
    
    Args:
        tableau: Tableau actuel du simplexe
        
    Returns:
        Indice de la variable entrante, ou None si optimal
    """
    reduced_costs = tableau.compute_reduced_costs()
    
    max_rc = Fraction(0)
    entering = None
    
    for j, rc in enumerate(reduced_costs):
        if rc > max_rc:
            max_rc = rc
            entering = j
    
    return entering


def find_leaving_variable(tableau: Tableau, entering: int) -> Optional[int]:
    """
    Trouve la variable sortante selon la règle du ratio minimum.
    
    Args:
        tableau: Tableau actuel du simplexe
        entering: Indice de la variable entrante
        
    Returns:
        Indice de la ligne pivot, ou None si non borné
    """
    min_ratio = None
    leaving = None
    
    for i in range(tableau.num_rows):
        aij = tableau.matrix[i][entering]
        
        if aij > 0:
            ratio = tableau.b[i] / aij
            
            if min_ratio is None or ratio < min_ratio:
                min_ratio = ratio
                leaving = i
    
    return leaving


def primal_simplex(
    tableau: Tableau,
    max_iterations: int = 1000,
    callback: Optional[Callable[[Tableau, int], None]] = None
) -> SimplexResult:
    """
    Exécute l'algorithme du simplexe primal.
    
    Args:
        tableau: Tableau initial
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
        # Vérifier l'optimalité
        if current.is_optimal_primal():
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
        entering = find_entering_variable(current)
        
        if entering is None:
            # Optimal (ne devrait pas arriver ici si is_optimal_primal est correct)
            z, _ = current.compute_z()
            return SimplexResult(
                status=SimplexStatus.OPTIMAL,
                tableau=current,
                objective_value=z,
                solution=current.get_original_solution(),
                iterations=iteration,
                history=history
            )
        
        # Trouver la variable sortante
        leaving = find_leaving_variable(current, entering)
        
        if leaving is None:
            # Problème non borné
            return SimplexResult(
                status=SimplexStatus.UNBOUNDED,
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


def solve_relaxed(problem: Problem, callback: Optional[Callable] = None) -> SimplexResult:
    """
    Résout le problème relaxé (sans contraintes d'intégrité).
    
    Args:
        problem: Problème PLNE à résoudre
        callback: Fonction de rappel pour le suivi
        
    Returns:
        Résultat du simplexe
    """
    # Créer le tableau initial
    tableau = create_initial_tableau(problem)
    
    # Résoudre avec le simplexe primal
    return primal_simplex(tableau, callback=callback)
