"""Tests pour le solveur complet."""

import pytest
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory import Problem, GomorySolver, SolverStatus


class TestGomorySolver:
    """Tests pour le solveur Gomory complet."""
    
    def test_knapsack_problem(self):
        """
        Teste le problème du sac à dos du cours.
        
        Solution attendue: x* = (0, 1, 1), z* = 15
        """
        problem = Problem(
            objective=[6, 8, 7],
            sense="max",
            constraints=[
                ([4, 6, 8], "<=", 14),
                ([1, 0, 0], "<=", 1),
                ([0, 1, 0], "<=", 1),
                ([0, 0, 1], "<=", 1),
            ],
            integer_vars=[0, 1, 2]
        )
        
        solver = GomorySolver(problem, verbose=False)
        result = solver.solve()
        
        assert result.status == SolverStatus.OPTIMAL_INTEGER
        assert result.optimal_value == Fraction(15)
        
        # La solution doit être (0, 1, 1)
        solution = result.solution
        assert solution[0] == 0
        assert solution[1] == 1
        assert solution[2] == 1
    
    def test_simple_integer_problem(self):
        """Teste un problème simple avec solution entière directe."""
        problem = Problem(
            objective=[1, 1],
            sense="max",
            constraints=[
                ([1, 0], "<=", 2),
                ([0, 1], "<=", 3),
            ],
            integer_vars=[0, 1]
        )
        
        solver = GomorySolver(problem, verbose=False)
        result = solver.solve()
        
        assert result.status == SolverStatus.OPTIMAL_INTEGER
        assert result.optimal_value == Fraction(5)  # 2 + 3 = 5
        assert result.solution == [Fraction(2), Fraction(3)]
        assert result.num_cuts == 0  # Pas de coupe nécessaire
    
    def test_problem_requiring_cuts(self):
        """Teste un problème nécessitant des coupes."""
        problem = Problem(
            objective=[5, 8],
            sense="max",
            constraints=[
                ([1, 1], "<=", 6),
                ([5, 9], "<=", 45),
            ],
            integer_vars=[0, 1]
        )
        
        solver = GomorySolver(problem, verbose=False)
        result = solver.solve()
        
        assert result.status == SolverStatus.OPTIMAL_INTEGER
        
        # Vérifier que la solution est entière
        for val in result.solution:
            assert val.denominator == 1
    
    def test_continuous_problem(self):
        """Teste un problème sans contraintes d'intégrité."""
        problem = Problem(
            objective=[3, 2],
            sense="max",
            constraints=[
                ([1, 1], "<=", 4),
                ([2, 1], "<=", 5),
            ],
            integer_vars=[]  # Pas de contraintes d'intégrité
        )
        
        solver = GomorySolver(problem, verbose=False)
        result = solver.solve()
        
        assert result.status == SolverStatus.OPTIMAL_CONTINUOUS
        assert result.num_cuts == 0


class TestSolverHistory:
    """Tests pour l'historique du solveur."""
    
    def test_history_is_recorded(self):
        """Teste que l'historique est bien enregistré."""
        problem = Problem(
            objective=[6, 8, 7],
            sense="max",
            constraints=[
                ([4, 6, 8], "<=", 14),
                ([1, 0, 0], "<=", 1),
                ([0, 1, 0], "<=", 1),
                ([0, 0, 1], "<=", 1),
            ],
            integer_vars=[0, 1, 2]
        )
        
        solver = GomorySolver(problem, verbose=False)
        result = solver.solve()
        
        # L'historique doit contenir plusieurs itérations
        assert len(result.history) > 0
        
        # Chaque itération doit avoir un tableau
        for iteration in result.history:
            assert iteration.tableau is not None
            assert iteration.phase in ["initialisation", "simplex_primal", 
                                       "coupe_gomory", "dual_simplex"]
