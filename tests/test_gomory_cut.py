"""Tests pour le module gomory_cut."""

import pytest
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory.problem import Problem
from gomory.simplex import create_initial_tableau, primal_simplex
from gomory.gomory_cut import find_cut_row, generate_gomory_cut, add_cut_to_tableau


class TestFindCutRow:
    """Tests pour la sélection de la ligne de coupe."""
    
    def test_find_row_with_fractional_solution(self):
        """Teste la sélection de la ligne avec la plus grande partie décimale."""
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
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        # Trouver la ligne pour la coupe
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        
        # Il doit y avoir une ligne avec solution fractionnaire
        assert cut_row is not None
    
    def test_no_cut_row_for_integer_solution(self):
        """Teste qu'aucune coupe n'est générée pour une solution entière."""
        problem = Problem(
            objective=[1, 1],
            sense="max",
            constraints=[
                ([1, 0], "<=", 2),
                ([0, 1], "<=", 3),
            ],
            integer_vars=[0, 1]
        )
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        # La solution est déjà entière (2, 3)
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        
        # Pas de coupe nécessaire
        assert cut_row is None


class TestGenerateGomoryCut:
    """Tests pour la génération des coupes de Gomory."""
    
    def test_cut_coefficients_are_fractional_parts(self):
        """Teste que les coefficients de la coupe sont basés sur les parties décimales."""
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
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        assert cut_row is not None
        
        cut = generate_gomory_cut(result.tableau, cut_row)
        
        # Vérifier que la partie décimale du RHS est correcte
        assert cut.fractional_rhs > 0
        assert cut.fractional_rhs < 1
        
        # Le RHS de la coupe doit être négatif (forme standard)
        assert cut.rhs < 0


class TestAddCutToTableau:
    """Tests pour l'ajout d'une coupe au tableau."""
    
    def test_tableau_dimensions_increase(self):
        """Teste que les dimensions du tableau augmentent correctement."""
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
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        original_rows = result.tableau.num_rows
        original_cols = result.tableau.num_cols
        
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        cut = generate_gomory_cut(result.tableau, cut_row)
        
        new_tableau = add_cut_to_tableau(result.tableau, cut)
        
        # Une nouvelle ligne et une nouvelle colonne
        assert new_tableau.num_rows == original_rows + 1
        assert new_tableau.num_cols == original_cols + 1
    
    def test_new_variable_in_basis(self):
        """Teste que la nouvelle variable d'écart est dans la base."""
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
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        cut = generate_gomory_cut(result.tableau, cut_row)
        
        new_tableau = add_cut_to_tableau(result.tableau, cut)
        
        # La nouvelle variable d'écart doit être dans la base
        new_var_idx = new_tableau.num_cols - 1
        assert new_var_idx in new_tableau.basis
