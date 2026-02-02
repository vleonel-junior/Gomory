"""
Exemple du problème du sac à dos - Application du cours.

Ce script reproduit exactement l'exemple du cours sur la méthode
des coupes de Gomory appliquée au problème du sac à dos.

Problème:
    Soit à remplir un sac ne pouvant supporter que 14kg, par un, deux ou trois 
    objets parmi les trois objets O₁, O₂, O₃ de poids respectifs 4 kg, 6 kg, 8 kg
    et de valeurs respectives 6, 8, 7, tout en maximisant la valeur totale des 
    objets placés dans le sac.

Modélisation:
    max z = 6x₁ + 8x₂ + 7x₃
    s.c.
        4x₁ + 6x₂ + 8x₃ ≤ 14
        x₁ ≤ 1
        x₂ ≤ 1
        x₃ ≤ 1
        x₁, x₂, x₃ ∈ ℕ

Solution attendue:
    x* = (0, 1, 1) avec z* = 15
    Choisir les objets O₂ et O₃
"""

import sys
import os

# Ajouter le répertoire parent au path pour l'import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomory import Problem, GomorySolver, display_tableau, display_cut


def main():
    print("=" * 70)
    print("MÉTHODE DES COUPES DE GOMORY - PROBLÈME DU SAC À DOS")
    print("=" * 70)
    print()
    
    # Description du problème
    print("ÉNONCÉ DU PROBLÈME")
    print("-" * 70)
    print("""
Soit à remplir un sac ne pouvant supporter que 14kg, par un, deux ou trois 
objets parmi les trois objets O₁, O₂, O₃:
    - O₁: poids = 4 kg, valeur = 6
    - O₂: poids = 6 kg, valeur = 8  
    - O₃: poids = 8 kg, valeur = 7

Objectif: Maximiser la valeur totale des objets dans le sac.

Soit xᵢ le nombre d'objets Oᵢ placés dans le sac (xᵢ ∈ {0, 1}).
""")
    
    print("MODÉLISATION")
    print("-" * 70)
    print("""
    max z = 6x₁ + 8x₂ + 7x₃
    
    sous contraintes:
        4x₁ + 6x₂ + 8x₃ ≤ 14   (contrainte de poids)
        x₁ ≤ 1                  (au plus un objet O₁)
        x₂ ≤ 1                  (au plus un objet O₂)
        x₃ ≤ 1                  (au plus un objet O₃)
        x₁, x₂, x₃ ∈ ℕ         (contraintes d'intégrité)
""")
    
    # Définir le problème
    problem = Problem(
        objective=[6, 8, 7],
        sense="max",
        constraints=[
            ([4, 6, 8], "<=", 14),  # Contrainte de poids
            ([1, 0, 0], "<=", 1),   # x₁ ≤ 1
            ([0, 1, 0], "<=", 1),   # x₂ ≤ 1
            ([0, 0, 1], "<=", 1),   # x₃ ≤ 1
        ],
        integer_vars=[0, 1, 2],  # x₁, x₂, x₃ doivent être entières
        var_names=["x1", "x2", "x3"]
    )
    
    print("RÉSOLUTION")
    print("-" * 70)
    print()
    
    # Créer le solveur avec affichage détaillé
    def display_callback(iteration):
        print(f"\n{'='*60}")
        print(f"Itération {iteration.iteration_number}: {iteration.phase}")
        print(f"{'='*60}")
        print(display_tableau(iteration.tableau, title=iteration.description))
        
        if iteration.cut:
            print(display_cut(iteration.cut, iteration.tableau.var_names))
    
    solver = GomorySolver(
        problem,
        verbose=True,
        display_callback=display_callback
    )
    
    # Résoudre
    result = solver.solve()
    
    # Afficher le résultat final
    print("\n")
    print("=" * 70)
    print("INTERPRÉTATION DU RÉSULTAT")
    print("=" * 70)
    print()
    print(result)
    print()
    
    if result.solution:
        x1, x2, x3 = result.solution[:3]
        print("Décision optimale:")
        if x1 == 1:
            print("  - Prendre l'objet O₁ (poids: 4kg, valeur: 6)")
        if x2 == 1:
            print("  - Prendre l'objet O₂ (poids: 6kg, valeur: 8)")
        if x3 == 1:
            print("  - Prendre l'objet O₃ (poids: 8kg, valeur: 7)")
        
        total_weight = 4 * x1 + 6 * x2 + 8 * x3
        total_value = 6 * x1 + 8 * x2 + 7 * x3
        print(f"\nPoids total: {total_weight} kg (capacité: 14 kg)")
        print(f"Valeur totale: {total_value}")


if __name__ == "__main__":
    main()
