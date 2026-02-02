"""
Module du tableau du simplexe.

Ce module fournit la classe Tableau qui représente le tableau du simplexe
et les opérations de pivot nécessaires à l'algorithme.
"""

from fractions import Fraction
from typing import List, Optional, Tuple, Dict
from copy import deepcopy

from .fraction_utils import to_fraction, to_fraction_list, is_integer, Numeric


class Tableau:
    """
    Représente un tableau du simplexe.
    
    Le tableau a la structure suivante (comme dans le cours):
    
    | Max | Ci  | c1  | c2  | ... | cn  | 0   | 0   | ... |
    | CB  | B   | b   | x1  | x2  | ... | xn  | s1  | ... |
    | cb1 | xB1 | b1  | a11 | a12 | ... | a1n | ... | ... |
    | cb2 | xB2 | b2  | a21 | a22 | ... | a2n | ... | ... |
    | ... | ... | ... | ... | ... | ... | ... | ... | ... |
    |     | Zi  | z   | z1  | z2  | ... | zn  | ... | ... |
    |     |Ci-Zi|     |c1-z1|c2-z2| ... |cn-zn| ... | ... |
    
    Attributes:
        matrix: Matrice des coefficients (lignes de contraintes)
        b: Vecteur des membres de droite
        c: Vecteur des coûts de la fonction objectif
        c_b: Coûts des variables de base
        basis: Indices des variables de base
        var_names: Noms de toutes les variables
        num_original_vars: Nombre de variables originales (sans les variables d'écart)
    """
    
    def __init__(
        self,
        matrix: List[List[Numeric]],
        b: List[Numeric],
        c: List[Numeric],
        basis: List[int],
        var_names: Optional[List[str]] = None,
        num_original_vars: Optional[int] = None
    ):
        """
        Initialise un tableau du simplexe.
        
        Args:
            matrix: Matrice des coefficients des contraintes
            b: Membres de droite
            c: Coefficients de la fonction objectif (pour toutes les variables)
            basis: Indices des variables de base
            var_names: Noms des variables
            num_original_vars: Nombre de variables originales
        """
        # Convertir en fractions
        self.matrix = [[to_fraction(val) for val in row] for row in matrix]
        self.b = [to_fraction(val) for val in b]
        self.c = [to_fraction(val) for val in c]
        self.basis = list(basis)
        
        # Calculer c_b (coûts des variables de base)
        self.c_b = [self.c[j] for j in self.basis]
        
        # Noms des variables
        n = len(c)
        if var_names is None:
            self.var_names = [f"x{i+1}" for i in range(n)]
        else:
            self.var_names = list(var_names)
        
        self.num_original_vars = num_original_vars if num_original_vars else n
    
    @property
    def num_rows(self) -> int:
        """Nombre de lignes (contraintes)."""
        return len(self.matrix)
    
    @property
    def num_cols(self) -> int:
        """Nombre de colonnes (variables)."""
        return len(self.c)
    
    def compute_z(self) -> Tuple[Fraction, List[Fraction]]:
        """
        Calcule z (valeur de la fonction objectif) et Zi (coûts marginaux).
        
        Returns:
            Tuple (z, Zi) où:
            - z: valeur actuelle de la fonction objectif
            - Zi: liste des coûts marginaux pour chaque variable
        """
        z = Fraction(0)
        for i, bi in enumerate(self.b):
            z += self.c_b[i] * bi
        
        # Calculer Zi pour chaque variable
        zi = []
        for j in range(self.num_cols):
            zj = Fraction(0)
            for i in range(self.num_rows):
                zj += self.c_b[i] * self.matrix[i][j]
            zi.append(zj)
        
        return z, zi
    
    def compute_reduced_costs(self) -> List[Fraction]:
        """
        Calcule les coûts réduits (Ci - Zi).
        
        Returns:
            Liste des coûts réduits pour chaque variable
        """
        _, zi = self.compute_z()
        return [self.c[j] - zi[j] for j in range(self.num_cols)]
    
    def get_solution(self) -> Dict[str, Fraction]:
        """
        Retourne la solution actuelle du tableau.
        
        Returns:
            Dictionnaire {nom_variable: valeur}
        """
        solution = {name: Fraction(0) for name in self.var_names}
        
        for i, basis_idx in enumerate(self.basis):
            solution[self.var_names[basis_idx]] = self.b[i]
        
        return solution
    
    def get_basic_solution_values(self) -> List[Tuple[str, Fraction]]:
        """
        Retourne les valeurs des variables de base.
        
        Returns:
            Liste de tuples (nom, valeur) pour les variables de base
        """
        return [(self.var_names[self.basis[i]], self.b[i]) 
                for i in range(self.num_rows)]
    
    def get_original_solution(self) -> List[Fraction]:
        """
        Retourne la solution pour les variables originales uniquement.
        
        Returns:
            Liste des valeurs pour les variables x1, x2, ..., xn
        """
        solution = [Fraction(0)] * self.num_original_vars
        
        for i, basis_idx in enumerate(self.basis):
            if basis_idx < self.num_original_vars:
                solution[basis_idx] = self.b[i]
        
        return solution
    
    def pivot(self, pivot_row: int, pivot_col: int) -> "Tableau":
        """
        Effectue une opération de pivot.
        
        Args:
            pivot_row: Indice de la ligne pivot
            pivot_col: Indice de la colonne pivot
            
        Returns:
            Nouveau tableau après pivot
        """
        # Créer une copie profonde
        new_tableau = deepcopy(self)
        
        # Élément pivot
        pivot_element = new_tableau.matrix[pivot_row][pivot_col]
        
        if pivot_element == 0:
            raise ValueError("L'élément pivot ne peut pas être zéro")
        
        # Diviser la ligne pivot par l'élément pivot
        for j in range(new_tableau.num_cols):
            new_tableau.matrix[pivot_row][j] /= pivot_element
        new_tableau.b[pivot_row] /= pivot_element
        
        # Éliminer dans les autres lignes
        for i in range(new_tableau.num_rows):
            if i != pivot_row:
                factor = new_tableau.matrix[i][pivot_col]
                for j in range(new_tableau.num_cols):
                    new_tableau.matrix[i][j] -= factor * new_tableau.matrix[pivot_row][j]
                new_tableau.b[i] -= factor * new_tableau.b[pivot_row]
        
        # Mettre à jour la base
        new_tableau.basis[pivot_row] = pivot_col
        new_tableau.c_b[pivot_row] = new_tableau.c[pivot_col]
        
        return new_tableau
    
    def add_variable(self, column: List[Numeric], cost: Numeric, name: str) -> "Tableau":
        """
        Ajoute une nouvelle variable (colonne) au tableau.
        
        Args:
            column: Coefficients de la nouvelle variable dans chaque contrainte
            cost: Coefficient dans la fonction objectif
            name: Nom de la variable
            
        Returns:
            Nouveau tableau avec la variable ajoutée
        """
        new_tableau = deepcopy(self)
        
        # Ajouter la colonne à la matrice
        column_frac = to_fraction_list(column)
        for i in range(new_tableau.num_rows):
            new_tableau.matrix[i].append(column_frac[i])
        
        # Ajouter le coût
        new_tableau.c.append(to_fraction(cost))
        
        # Ajouter le nom
        new_tableau.var_names.append(name)
        
        return new_tableau
    
    def add_constraint_row(
        self,
        row: List[Numeric],
        rhs: Numeric,
        basis_var_index: int
    ) -> "Tableau":
        """
        Ajoute une nouvelle contrainte (ligne) au tableau.
        
        Args:
            row: Coefficients de la nouvelle contrainte
            rhs: Membre de droite
            basis_var_index: Indice de la variable de base pour cette ligne
            
        Returns:
            Nouveau tableau avec la contrainte ajoutée
        """
        new_tableau = deepcopy(self)
        
        # Ajouter la ligne
        new_tableau.matrix.append(to_fraction_list(row))
        new_tableau.b.append(to_fraction(rhs))
        
        # Ajouter à la base
        new_tableau.basis.append(basis_var_index)
        new_tableau.c_b.append(new_tableau.c[basis_var_index])
        
        return new_tableau
    
    def is_feasible(self) -> bool:
        """
        Vérifie si la solution de base actuelle est réalisable.
        
        Une solution est réalisable si tous les bi >= 0.
        
        Returns:
            True si réalisable, False sinon
        """
        return all(bi >= 0 for bi in self.b)
    
    def is_optimal_primal(self) -> bool:
        """
        Vérifie si le tableau est optimal pour le simplexe primal.
        
        Optimal si tous les coûts réduits (Ci - Zi) <= 0 (pour maximisation).
        
        Returns:
            True si optimal, False sinon
        """
        reduced_costs = self.compute_reduced_costs()
        return all(rc <= 0 for rc in reduced_costs)
    
    def is_optimal_dual(self) -> bool:
        """
        Vérifie si le tableau est optimal pour le simplexe dual.
        
        Le dual est optimal quand la solution est réalisable (bi >= 0).
        
        Returns:
            True si optimal, False sinon
        """
        return self.is_feasible()
    
    def has_integer_solution(self, integer_vars: List[int]) -> bool:
        """
        Vérifie si la solution actuelle est entière pour les variables spécifiées.
        
        Args:
            integer_vars: Indices des variables qui doivent être entières
            
        Returns:
            True si toutes les variables spécifiées sont entières
        """
        solution = self.get_original_solution()
        
        for var_idx in integer_vars:
            if var_idx < len(solution):
                if not is_integer(solution[var_idx]):
                    return False
        
        return True
    
    def copy(self) -> "Tableau":
        """Retourne une copie profonde du tableau."""
        return deepcopy(self)
    
    def __str__(self) -> str:
        """Représentation textuelle simple du tableau."""
        lines = []
        lines.append(f"Base: {[self.var_names[i] for i in self.basis]}")
        lines.append(f"b: {[str(bi) for bi in self.b]}")
        z, _ = self.compute_z()
        lines.append(f"z = {z}")
        return "\n".join(lines)
