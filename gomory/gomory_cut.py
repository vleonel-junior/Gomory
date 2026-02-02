"""
Génération des coupes de Gomory.

Ce module implémente la génération des coupes de Gomory à partir
d'un tableau du simplexe avec une solution fractionnaire.
"""

from fractions import Fraction
from typing import Optional, Tuple, List
from dataclasses import dataclass

from .tableau import Tableau
from .fraction_utils import fractional_part, is_integer


@dataclass
class GomoryCut:
    """
    Représente une coupe de Gomory.
    
    La coupe a la forme:
    Σ {a_kp} * x_p >= {b_k}
    
    Qui est convertie en:
    -Σ {a_kp} * x_p + s = -{b_k}
    
    Où s est la nouvelle variable d'écart.
    
    Attributes:
        source_row: Indice de la ligne source dans le tableau
        source_var: Nom de la variable de base source
        coefficients: Coefficients de la coupe (pour les variables hors base)
        rhs: Membre de droite de la coupe
        fractional_parts: Parties décimales des coefficients originaux
        fractional_rhs: Partie décimale du membre de droite original
    """
    source_row: int
    source_var: str
    coefficients: List[Fraction]  # Coefficients pour TOUTES les variables
    rhs: Fraction
    fractional_parts: List[Fraction]
    fractional_rhs: Fraction


def find_cut_row(tableau: Tableau, integer_vars: List[int]) -> Optional[int]:
    """
    Trouve la ligne pour générer la coupe de Gomory.
    
    Selon le cours, on choisit la ligne avec la plus grande partie décimale
    parmi les variables de base qui devraient être entières mais ne le sont pas.
    
    Args:
        tableau: Tableau du simplexe
        integer_vars: Indices des variables qui doivent être entières
        
    Returns:
        Indice de la ligne à utiliser, ou None si solution entière
    """
    max_frac = Fraction(0)
    best_row = None
    
    for i in range(tableau.num_rows):
        basis_var = tableau.basis[i]
        
        # Vérifier si cette variable de base doit être entière
        if basis_var in integer_vars:
            bi = tableau.b[i]
            frac_part = fractional_part(bi)
            
            if frac_part > 0 and frac_part > max_frac:
                max_frac = frac_part
                best_row = i
    
    return best_row


def generate_gomory_cut(tableau: Tableau, source_row: int) -> GomoryCut:
    """
    Génère une coupe de Gomory à partir d'une ligne du tableau.
    
    Selon le cours, pour la ligne k:
    x_k + Σ ã_kp * x_p = b̃_k
    
    La coupe est:
    Σ {ã_kp} * x_p >= {b̃_k}
    
    Ce qui devient (sous forme standard avec variable d'écart):
    -Σ {ã_kp} * x_p + s = -{b̃_k}
    
    Attention: Pour les coefficients négatifs, {a} = a - ⌊a⌋
    Par exemple: {-1/2} = -1/2 - (-1) = 1/2
    
    Args:
        tableau: Tableau du simplexe
        source_row: Indice de la ligne source
        
    Returns:
        Coupe de Gomory générée
    """
    n_cols = tableau.num_cols
    
    # Partie décimale du membre de droite
    b_k = tableau.b[source_row]
    frac_b = fractional_part(b_k)
    
    # Parties décimales des coefficients
    frac_coeffs = []
    for j in range(n_cols):
        a_kj = tableau.matrix[source_row][j]
        frac_a = fractional_part(a_kj)
        frac_coeffs.append(frac_a)
    
    # Coefficients de la coupe (forme standard: -frac pour avoir <=)
    # La contrainte Σ {a_kp} x_p >= {b_k}
    # Devient: -Σ {a_kp} x_p <= -{b_k}
    # Puis: -Σ {a_kp} x_p + s = -{b_k}
    cut_coeffs = [-frac for frac in frac_coeffs]
    cut_rhs = -frac_b
    
    return GomoryCut(
        source_row=source_row,
        source_var=tableau.var_names[tableau.basis[source_row]],
        coefficients=cut_coeffs,
        rhs=cut_rhs,
        fractional_parts=frac_coeffs,
        fractional_rhs=frac_b
    )


def add_cut_to_tableau(tableau: Tableau, cut: GomoryCut) -> Tableau:
    """
    Ajoute une coupe de Gomory au tableau du simplexe.
    
    Cela implique:
    1. Ajouter une nouvelle variable d'écart
    2. Ajouter une nouvelle ligne pour la coupe
    
    Args:
        tableau: Tableau original
        cut: Coupe à ajouter
        
    Returns:
        Nouveau tableau avec la coupe ajoutée
    """
    # Copier le tableau
    new_tableau = tableau.copy()
    
    # Index de la nouvelle variable d'écart
    new_var_idx = new_tableau.num_cols
    new_var_name = f"x{new_var_idx + 1}"
    
    # 1. Ajouter une colonne pour la nouvelle variable d'écart
    # Cette variable a un coefficient de 0 partout sauf dans la nouvelle ligne
    for i in range(new_tableau.num_rows):
        new_tableau.matrix[i].append(Fraction(0))
    
    # Ajouter le coût (0 pour variable d'écart)
    new_tableau.c.append(Fraction(0))
    new_tableau.var_names.append(new_var_name)
    
    # 2. Ajouter la nouvelle ligne
    # Les coefficients sont ceux de la coupe + 1 pour la variable d'écart
    new_row = list(cut.coefficients)
    new_row.append(Fraction(1))  # Coefficient de la nouvelle variable d'écart
    
    new_tableau.matrix.append(new_row)
    new_tableau.b.append(cut.rhs)
    new_tableau.basis.append(new_var_idx)
    new_tableau.c_b.append(Fraction(0))
    
    return new_tableau


def format_cut(cut: GomoryCut, var_names: List[str]) -> str:
    """
    Formate une coupe de Gomory pour l'affichage.
    
    Args:
        cut: Coupe à formater
        var_names: Noms des variables
        
    Returns:
        Représentation textuelle de la coupe
    """
    lines = []
    
    # Équation originale
    lines.append(f"Ligne source: {cut.source_var} (ligne {cut.source_row})")
    
    # Afficher la forme >= (avant transformation)
    terms_geq = []
    for j, frac in enumerate(cut.fractional_parts):
        if frac != 0:
            terms_geq.append(f"({frac})*{var_names[j]}")
    
    if terms_geq:
        lines.append(f"Coupe: {' + '.join(terms_geq)} >= {cut.fractional_rhs}")
    
    # Afficher la forme <= (après multiplication par -1)
    terms_leq = []
    for j, coef in enumerate(cut.coefficients):
        if coef != 0:
            terms_leq.append(f"({coef})*{var_names[j]}")
    
    if terms_leq:
        lines.append(f"Soit:  {' + '.join(terms_leq)} <= {cut.rhs}")
    
    return "\n".join(lines)
