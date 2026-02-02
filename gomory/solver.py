"""
Solveur principal pour la méthode des coupes de Gomory.

Ce module orchestre l'ensemble de l'algorithme:
1. Résolution du programme linéaire relaxé
2. Génération des coupes de Gomory si nécessaire
3. Application du dual simplexe
4. Itération jusqu'à obtention d'une solution entière
"""

from fractions import Fraction
from typing import Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

from .problem import Problem, Sense
from .tableau import Tableau
from .simplex import create_initial_tableau, primal_simplex, SimplexStatus
from .dual_simplex import dual_simplex
from .gomory_cut import find_cut_row, generate_gomory_cut, add_cut_to_tableau, GomoryCut


class SolverStatus(Enum):
    """Statut final du solveur."""
    OPTIMAL_INTEGER = "solution entière optimale trouvée"
    OPTIMAL_CONTINUOUS = "solution continue optimale (aucune variable entière requise)"
    UNBOUNDED = "problème non borné"
    INFEASIBLE = "problème non réalisable"
    MAX_ITERATIONS = "nombre maximal d'itérations atteint"
    MAX_CUTS = "nombre maximal de coupes atteint"


@dataclass
class Iteration:
    """
    Représente une itération de l'algorithme.
    
    Attributes:
        iteration_number: Numéro de l'itération
        phase: Phase de l'algorithme ("simplex_primal", "coupe_gomory", "dual_simplex")
        tableau: Tableau à cette étape
        cut: Coupe générée (si applicable)
        description: Description de l'étape
    """
    iteration_number: int
    phase: str
    tableau: Tableau
    cut: Optional[GomoryCut] = None
    description: str = ""


@dataclass
class SolverResult:
    """
    Résultat complet du solveur.
    
    Attributes:
        status: Statut final
        optimal_value: Valeur optimale de la fonction objectif
        solution: Solution optimale (valeurs des variables originales)
        solution_dict: Solution sous forme de dictionnaire
        total_iterations: Nombre total d'itérations
        num_cuts: Nombre de coupes ajoutées
        history: Historique de toutes les itérations
        final_tableau: Tableau final
    """
    status: SolverStatus
    optimal_value: Optional[Fraction] = None
    solution: Optional[List[Fraction]] = None
    solution_dict: Optional[dict] = None
    total_iterations: int = 0
    num_cuts: int = 0
    history: List[Iteration] = field(default_factory=list)
    final_tableau: Optional[Tableau] = None
    
    def __str__(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("RÉSULTAT FINAL")
        lines.append("=" * 60)
        lines.append(f"Statut: {self.status.value}")
        
        if self.optimal_value is not None:
            lines.append(f"Valeur optimale z* = {self.optimal_value}")
        
        if self.solution_dict:
            lines.append("Solution optimale:")
            for var, val in self.solution_dict.items():
                if not var.startswith("x") or int(var[1:]) <= len(self.solution):
                    # Afficher seulement les variables originales
                    pass
            # Afficher les variables originales
            for i, val in enumerate(self.solution):
                lines.append(f"  x{i+1} = {val}")
        
        lines.append(f"Nombre de coupes de Gomory: {self.num_cuts}")
        lines.append(f"Nombre total d'itérations: {self.total_iterations}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


class GomorySolver:
    """
    Solveur pour les programmes linéaires en nombres entiers
    utilisant la méthode des coupes de Gomory.
    
    Example:
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
        >>> solver = GomorySolver(problem, verbose=True)
        >>> result = solver.solve()
    """
    
    def __init__(
        self,
        problem: Problem,
        verbose: bool = False,
        max_iterations: int = 100,
        max_cuts: int = 50,
        display_callback: Optional[Callable] = None
    ):
        """
        Initialise le solveur.
        
        Args:
            problem: Problème PLNE à résoudre
            verbose: Si True, affiche les étapes
            max_iterations: Nombre maximal d'itérations du simplexe
            max_cuts: Nombre maximal de coupes de Gomory
            display_callback: Fonction de rappel pour l'affichage personnalisé
        """
        self.problem = problem
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.max_cuts = max_cuts
        self.display_callback = display_callback
        self.history: List[Iteration] = []
        self.iteration_count = 0
        self.is_minimization = (problem.sense == Sense.MINIMIZE)
    
    def _log(self, message: str) -> None:
        """Affiche un message si verbose est activé."""
        if self.verbose:
            print(message)
    
    def _convert_objective(self, z: Fraction) -> Fraction:
        """Convertit la valeur objectif si le problème original est une minimisation."""
        if self.is_minimization:
            return -z
        return z
    
    def _add_iteration(
        self,
        phase: str,
        tableau: Tableau,
        cut: Optional[GomoryCut] = None,
        description: str = ""
    ) -> None:
        """Ajoute une itération à l'historique."""
        self.iteration_count += 1
        iteration = Iteration(
            iteration_number=self.iteration_count,
            phase=phase,
            tableau=tableau.copy(),
            cut=cut,
            description=description
        )
        self.history.append(iteration)
        
        if self.display_callback:
            self.display_callback(iteration)
    
    def solve(self) -> SolverResult:
        """
        Résout le problème PLNE par la méthode des coupes de Gomory.
        
        Returns:
            Résultat de la résolution
        """
        self._log("=" * 60)
        self._log("RÉSOLUTION PAR LA MÉTHODE DES COUPES DE GOMORY")
        self._log("=" * 60)
        self._log("")
        self._log(str(self.problem))
        self._log("")
        
        # Convertir minimisation en maximisation si nécessaire
        # min z = c'x ⇔ max z' = -c'x, puis z = -z'
        working_problem = self.problem
        if self.is_minimization:
            self._log("Note: Conversion min → max (on multiplie l'objectif par -1)")
            self._log("")
            from .problem import Problem as ProblemClass
            working_problem = ProblemClass(
                objective=[-c for c in self.problem.objective],
                sense="max",
                constraints=[
                    (list(ctr.coefficients), ctr.constraint_type.value, ctr.rhs)
                    for ctr in self.problem.constraints
                ],
                integer_vars=self.problem.integer_vars,
                var_names=self.problem.var_names
            )
        
        # Étape 1: Créer le tableau initial
        self._log("Étape 1: Création du tableau initial (forme standard)")
        tableau = create_initial_tableau(working_problem)
        self._add_iteration("initialisation", tableau, description="Tableau initial")
        
        # Étape 2: Résoudre le problème relaxé avec le simplexe primal
        self._log("\nÉtape 2: Résolution du problème relaxé (simplexe primal)")
        
        def simplex_callback(tab: Tableau, it: int):
            if it > 0:
                self._add_iteration(
                    "simplex_primal",
                    tab,
                    description=f"Itération {it} du simplexe primal"
                )
        
        result = primal_simplex(tableau, self.max_iterations, callback=simplex_callback)
        
        if result.status == SimplexStatus.UNBOUNDED:
            return SolverResult(
                status=SolverStatus.UNBOUNDED,
                history=self.history,
                total_iterations=self.iteration_count
            )
        
        if result.status != SimplexStatus.OPTIMAL:
            return SolverResult(
                status=SolverStatus.INFEASIBLE,
                history=self.history,
                total_iterations=self.iteration_count
            )
        
        tableau = result.tableau
        self._log(f"\nSolution relaxée: z = {result.objective_value}")
        self._log(f"x = {result.solution}")
        
        # Si pas de contraintes d'intégrité, on a terminé
        if not self.problem.integer_vars:
            return SolverResult(
                status=SolverStatus.OPTIMAL_CONTINUOUS,
                optimal_value=self._convert_objective(result.objective_value),
                solution=result.solution,
                solution_dict=tableau.get_solution(),
                total_iterations=self.iteration_count,
                num_cuts=0,
                history=self.history,
                final_tableau=tableau
            )
        
        # Étape 3: Boucle des coupes de Gomory
        num_cuts = 0
        
        while num_cuts < self.max_cuts:
            # Vérifier si la solution est entière
            if tableau.has_integer_solution(self.problem.integer_vars):
                self._log("\n" + "=" * 60)
                self._log("SOLUTION ENTIÈRE TROUVÉE !")
                self._log("=" * 60)
                
                z, _ = tableau.compute_z()
                solution = tableau.get_original_solution()
                
                return SolverResult(
                    status=SolverStatus.OPTIMAL_INTEGER,
                    optimal_value=self._convert_objective(z),
                    solution=solution[:self.problem.num_variables],
                    solution_dict=tableau.get_solution(),
                    total_iterations=self.iteration_count,
                    num_cuts=num_cuts,
                    history=self.history,
                    final_tableau=tableau
                )
            
            # Trouver la ligne pour la coupe
            cut_row = find_cut_row(tableau, self.problem.integer_vars)
            
            if cut_row is None:
                # Solution entière (ne devrait pas arriver si has_integer_solution est correct)
                z, _ = tableau.compute_z()
                return SolverResult(
                    status=SolverStatus.OPTIMAL_INTEGER,
                    optimal_value=self._convert_objective(z),
                    solution=tableau.get_original_solution()[:self.problem.num_variables],
                    solution_dict=tableau.get_solution(),
                    total_iterations=self.iteration_count,
                    num_cuts=num_cuts,
                    history=self.history,
                    final_tableau=tableau
                )
            
            # Générer la coupe
            self._log(f"\nÉtape {3 + num_cuts * 2}: Génération de la coupe de Gomory #{num_cuts + 1}")
            cut = generate_gomory_cut(tableau, cut_row)
            
            self._log(f"  Ligne source: {cut.source_var} (b = {tableau.b[cut_row]})")
            self._log(f"  Partie décimale: {cut.fractional_rhs}")
            
            # Ajouter la coupe au tableau
            tableau = add_cut_to_tableau(tableau, cut)
            num_cuts += 1
            
            self._add_iteration(
                "coupe_gomory",
                tableau,
                cut=cut,
                description=f"Ajout de la coupe de Gomory #{num_cuts}"
            )
            
            self._log(f"  Nouvelle variable d'écart: x{tableau.num_cols}")
            self._log(f"  La solution n'est plus réalisable (b < 0)")
            
            # Appliquer le dual simplexe
            self._log(f"\nÉtape {4 + (num_cuts - 1) * 2}: Application du dual simplexe")
            
            def dual_callback(tab: Tableau, it: int):
                if it > 0:
                    self._add_iteration(
                        "dual_simplex",
                        tab,
                        description=f"Itération {it} du dual simplexe"
                    )
            
            result = dual_simplex(tableau, self.max_iterations, callback=dual_callback)
            
            if result.status == SimplexStatus.INFEASIBLE:
                return SolverResult(
                    status=SolverStatus.INFEASIBLE,
                    history=self.history,
                    total_iterations=self.iteration_count,
                    num_cuts=num_cuts
                )
            
            tableau = result.tableau
            z, _ = tableau.compute_z()
            self._log(f"  Nouvelle solution: z = {z}")
        
        # Nombre maximal de coupes atteint
        z, _ = tableau.compute_z()
        return SolverResult(
            status=SolverStatus.MAX_CUTS,
            optimal_value=self._convert_objective(z),
            solution=tableau.get_original_solution()[:self.problem.num_variables],
            solution_dict=tableau.get_solution(),
            total_iterations=self.iteration_count,
            num_cuts=num_cuts,
            history=self.history,
            final_tableau=tableau
        )
