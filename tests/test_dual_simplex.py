"""Tests pour le module dual_simplex."""

import pytest
from fractions import Fraction

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory.problem import Problem
from gomory.simplex import create_initial_tableau, primal_simplex, SimplexStatus
from gomory.dual_simplex import dual_simplex
from gomory.gomory_cut import find_cut_row, generate_gomory_cut, add_cut_to_tableau


class TestDualSimplex:
    """Tests pour l'algorithme dual du simplexe."""
    
    def test_dual_simplex_after_cut(self):
        """
        Teste que le dual simplexe restaure la faisabilité après une coupe.
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
        
        # Résoudre le problème relaxé
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        assert result.status == SimplexStatus.OPTIMAL
        
        # Générer et ajouter une coupe
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        cut = generate_gomory_cut(result.tableau, cut_row)
        tableau_with_cut = add_cut_to_tableau(result.tableau, cut)
        
        # Le tableau n'est plus réalisable (certains bi < 0)
        assert not tableau_with_cut.is_feasible()
        
        # Appliquer le dual simplexe
        dual_result = dual_simplex(tableau_with_cut)
        
        # Le dual simplexe doit restaurer la faisabilité
        assert dual_result.status == SimplexStatus.OPTIMAL
        assert dual_result.tableau.is_feasible()
    
    def test_dual_maintains_optimality(self):
        """
        Teste que le dual simplexe maintient l'optimalité duale.
        
        Après chaque itération, tous les coûts réduits doivent rester <= 0.
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
        
        tableau = create_initial_tableau(problem)
        result = primal_simplex(tableau)
        
        cut_row = find_cut_row(result.tableau, problem.integer_vars)
        cut = generate_gomory_cut(result.tableau, cut_row)
        tableau_with_cut = add_cut_to_tableau(result.tableau, cut)
        
        dual_result = dual_simplex(tableau_with_cut)
        
        # Vérifier l'optimalité duale (coûts réduits <= 0)
        reduced_costs = dual_result.tableau.compute_reduced_costs()
        for rc in reduced_costs:
            assert rc <= 0, f"Coût réduit positif trouvé: {rc}"
