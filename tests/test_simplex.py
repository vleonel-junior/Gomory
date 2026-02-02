"""Tests pour le module simplex."""

import pytest
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory.problem import Problem
from gomory.simplex import create_initial_tableau, primal_simplex, SimplexStatus


class TestCreateInitialTableau:
    """Tests pour la création du tableau initial."""
    
    def test_simple_problem(self):
        """Teste la création d'un tableau pour un problème simple."""
        problem = Problem(
            objective=[3, 2],
            sense="max",
            constraints=[
                ([1, 1], "<=", 4),
                ([2, 1], "<=", 5),
            ]
        )
        
        tableau = create_initial_tableau(problem)
        
        # Vérifier les dimensions
        assert tableau.num_rows == 2
        assert tableau.num_cols == 4  # 2 originales + 2 écart
        
        # Vérifier les coefficients objectifs
        assert tableau.c == [Fraction(3), Fraction(2), Fraction(0), Fraction(0)]
        
        # Vérifier les membres de droite
        assert tableau.b == [Fraction(4), Fraction(5)]
        
        # Vérifier la base initiale (variables d'écart)
        assert tableau.basis == [2, 3]


class TestPrimalSimplex:
    """Tests pour l'algorithme du simplexe primal."""
    
    def test_simple_maximization(self):
        """Teste un problème de maximisation simple."""
        problem = Problem(
            objective=[3, 2],
            sense="max",
            constraints=[
                ([1, 1], "<=", 4),
                ([2, 1], "<=", 5),
            ]
        )
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        assert result.status == SimplexStatus.OPTIMAL
        assert result.objective_value == Fraction(9)  # z* = 9
        
    def test_knapsack_relaxed(self):
        """Teste le problème du sac à dos relaxé (comme dans le cours)."""
        problem = Problem(
            objective=[6, 8, 7],
            sense="max",
            constraints=[
                ([4, 6, 8], "<=", 14),
                ([1, 0, 0], "<=", 1),
                ([0, 1, 0], "<=", 1),
                ([0, 0, 1], "<=", 1),
            ]
        )
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        assert result.status == SimplexStatus.OPTIMAL
        # La solution relaxée est z* = 35/2 = 17.5
        assert result.objective_value == Fraction(35, 2)
        
        # Vérifier la solution
        solution = result.solution
        assert solution[0] == Fraction(1)      # x1 = 1
        assert solution[1] == Fraction(1)      # x2 = 1
        assert solution[2] == Fraction(1, 2)   # x3 = 1/2
    
    def test_optimal_found(self):
        """Teste qu'une solution optimale est bien trouvée."""
        problem = Problem(
            objective=[1, 2],
            sense="max",
            constraints=[
                ([1, 0], "<=", 3),
                ([0, 1], "<=", 4),
            ]
        )
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        assert result.status == SimplexStatus.OPTIMAL
        assert result.objective_value == Fraction(11)  # z* = 1*3 + 2*4 = 11
        assert result.solution == [Fraction(3), Fraction(4)]
