#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exemple de minimisation avec la methode des coupes de Gomory.

Probleme (P):
    min z = -8*x1 - 5*x2
    
    sous contraintes:
        x1 + x2 <= 6
        9*x1 + 5*x2 <= 45
        x1, x2 >= 0 et entiers
"""

import sys
import os

# Ajouter le repertoire parent au path pour l'import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory import Problem, GomorySolver, display_tableau, display_cut


def main():
    print("=" * 70)
    print("METHODE DES COUPES DE GOMORY - PROBLEME DE MINIMISATION")
    print("=" * 70)
    print()
    
    print("ENONCE DU PROBLEME (P)")
    print("-" * 70)
    print("""
    min z = -8*x1 - 5*x2
    
    sous contraintes:
        x1 + x2 <= 6
        9*x1 + 5*x2 <= 45
        x1, x2 >= 0 et entiers
""")
    
    # Definir le probleme
    problem = Problem(
        objective=[-8, -5],
        sense="min",
        constraints=[
            ([1, 1], "<=", 6),      # x1 + x2 <= 6
            ([9, 5], "<=", 45),     # 9*x1 + 5*x2 <= 45
        ],
        integer_vars=[0, 1],  # x1, x2 doivent etre entieres
        var_names=["x1", "x2"]
    )
    
    print("RESOLUTION")
    print("-" * 70)
    print()
    
    # Creer le solveur avec affichage detaille des tableaux
    def display_callback(iteration):
        print(f"\n{'='*60}")
        print(f"Iteration {iteration.iteration_number}: {iteration.phase}")
        print(f"{'='*60}")
        print(display_tableau(iteration.tableau, title=iteration.description))
        
        if iteration.cut:
            print(display_cut(iteration.cut, iteration.tableau.var_names))
    
    solver = GomorySolver(
        problem,
        verbose=True,
        display_callback=display_callback
    )
    result = solver.solve()
    
    print()
    print("=" * 70)
    print("INTERPRETATION DU RESULTAT")
    print("=" * 70)
    print()
    
    if result.status == "optimal":
        print(f"Solution optimale entiere trouvee!")
        print(f"  x1* = {result.solution[0]}")
        print(f"  x2* = {result.solution[1]}")
        print(f"  z*  = {result.objective_value}")
        print()
        print(f"Nombre de coupes de Gomory: {result.cuts_added}")
        print(f"Nombre total d'iterations: {result.iterations}")
    elif result.solution:
        print(f"Solution optimale entiere trouvee!")
        print(f"  x1* = {result.solution[0]}")
        print(f"  x2* = {result.solution[1]}")
        print(f"  z*  = {result.optimal_value}")
        print()
        print(f"Nombre de coupes de Gomory: {result.num_cuts}")
        print(f"Nombre total d'iterations: {result.total_iterations}")
    else:
        print(f"Statut: {result.status}")


if __name__ == "__main__":
    main()
