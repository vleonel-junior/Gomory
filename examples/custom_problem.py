"""
Exemple personnalisé - Comment utiliser le package Gomory.

Ce script montre comment définir et résoudre un problème personnalisé
de programmation linéaire en nombres entiers avec le package Gomory.
"""

import sys
import os

# Ajouter le répertoire parent au path pour l'import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory import Problem, GomorySolver


def solve_custom_problem():
    """
    Exemple de résolution d'un problème personnalisé.
    
    max z = 3x₁ + 2x₂
    s.c.
        2x₁ + x₂ ≤ 6
        x₁ + 2x₂ ≤ 6
        x₁, x₂ ∈ ℕ
    """
    print("=" * 60)
    print("EXEMPLE PERSONNALISÉ")
    print("=" * 60)
    print()
    
    # Définir le problème
    problem = Problem(
        objective=[3, 2],
        sense="max",
        constraints=[
            ([2, 1], "<=", 6),
            ([1, 2], "<=", 6),
        ],
        integer_vars=[0, 1],
        var_names=["x1", "x2"]
    )
    
    print("Problème:")
    print(problem)
    print()
    
    # Résoudre
    solver = GomorySolver(problem, verbose=True)
    result = solver.solve()
    
    print()
    print(result)


def solve_production_problem():
    """
    Problème de production avec contraintes de ressources.
    
    Une entreprise fabrique deux produits P₁ et P₂.
    - P₁ nécessite 2h de machine A et 1h de machine B, profit: 5€
    - P₂ nécessite 1h de machine A et 3h de machine B, profit: 4€
    - Machine A: 8h disponibles
    - Machine B: 9h disponibles
    - On ne peut produire que des quantités entières
    
    max z = 5x₁ + 4x₂
    s.c.
        2x₁ + x₂ ≤ 8   (machine A)
        x₁ + 3x₂ ≤ 9   (machine B)
        x₁, x₂ ∈ ℕ
    """
    print()
    print("=" * 60)
    print("PROBLÈME DE PRODUCTION")
    print("=" * 60)
    print()
    
    problem = Problem(
        objective=[5, 4],
        sense="max",
        constraints=[
            ([2, 1], "<=", 8),  # Contrainte machine A
            ([1, 3], "<=", 9),  # Contrainte machine B
        ],
        integer_vars=[0, 1],
        var_names=["P1", "P2"]
    )
    
    print("Problème:")
    print(problem)
    print()
    
    solver = GomorySolver(problem, verbose=True)
    result = solver.solve()
    
    print()
    print(result)
    
    if result.solution:
        p1, p2 = result.solution[:2]
        print(f"\nDécision optimale:")
        print(f"  Produire {p1} unités de P₁")
        print(f"  Produire {p2} unités de P₂")
        print(f"  Profit total: {5*p1 + 4*p2}€")


def main():
    solve_custom_problem()
    solve_production_problem()


if __name__ == "__main__":
    main()
