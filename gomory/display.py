"""
Module d'affichage des tableaux du simplexe.

Ce module fournit des fonctions pour afficher les tableaux
du simplexe de manière formatée, similaire au style du cours.
"""

from fractions import Fraction
from typing import List, Optional

from .tableau import Tableau
from .fraction_utils import format_fraction
from .gomory_cut import GomoryCut


def format_cell(value: Fraction, width: int = 8) -> str:
    """
    Formate une cellule du tableau.
    
    Args:
        value: Valeur à formater
        width: Largeur de la cellule
        
    Returns:
        Chaîne formatée
    """
    s = format_fraction(value)
    return s.center(width)


def display_tableau(
    tableau: Tableau,
    title: str = "",
    show_reduced_costs: bool = True,
    highlight_pivot: Optional[tuple] = None
) -> str:
    """
    Affiche un tableau du simplexe de manière formatée.
    
    Reproduit le format du cours:
    
    | Max | Ci    | c1  | c2  | ... |
    | CB  | B     | b   | x1  | x2  | ... |
    | cb1 | xB1   | b1  | a11 | a12 | ... |
    | ... | ...   | ... | ... | ... | ... |
    |     | Zi    | z   | z1  | z2  | ... |
    |     | Ci-Zi |     | r1  | r2  | ... |
    
    Args:
        tableau: Tableau à afficher
        title: Titre du tableau
        show_reduced_costs: Si True, affiche la ligne Ci-Zi
        highlight_pivot: Tuple (row, col) pour surligner l'élément pivot
        
    Returns:
        Chaîne représentant le tableau formaté
    """
    lines = []
    cell_width = 10
    
    # Titre
    if title:
        lines.append("")
        lines.append("=" * (cell_width * (tableau.num_cols + 3)))
        lines.append(title.center(cell_width * (tableau.num_cols + 3)))
        lines.append("=" * (cell_width * (tableau.num_cols + 3)))
    
    # Calculs
    z, zi = tableau.compute_z()
    reduced_costs = tableau.compute_reduced_costs()
    
    # Ligne d'en-tête avec les Ci
    header_ci = ["Max", "Ci"]
    for j in range(tableau.num_cols):
        header_ci.append(format_fraction(tableau.c[j]))
    
    # Ligne d'en-tête avec les noms de variables
    header_vars = ["CB", "B", "b"]
    for j in range(tableau.num_cols):
        header_vars.append(tableau.var_names[j])
    
    # Construire les lignes du tableau
    table_rows = []
    
    # En-tête Ci
    table_rows.append(header_ci)
    
    # En-tête variables
    table_rows.append(header_vars)
    
    # Lignes de données
    for i in range(tableau.num_rows):
        row = []
        row.append(format_fraction(tableau.c_b[i]))  # CB
        row.append(tableau.var_names[tableau.basis[i]])  # B
        row.append(format_fraction(tableau.b[i]))  # b
        
        for j in range(tableau.num_cols):
            val = format_fraction(tableau.matrix[i][j])
            # Marquer le pivot
            if highlight_pivot and highlight_pivot == (i, j):
                val = f"[{val}]"
            row.append(val)
        
        table_rows.append(row)
    
    # Ligne Zi
    zi_row = ["", "Zi", format_fraction(z)]
    for j in range(tableau.num_cols):
        zi_row.append(format_fraction(zi[j]))
    table_rows.append(zi_row)
    
    # Ligne Ci - Zi
    if show_reduced_costs:
        rc_row = ["", "", "Ci-Zi"]
        for j in range(tableau.num_cols):
            rc_row.append(format_fraction(reduced_costs[j]))
        table_rows.append(rc_row)
    
    # Trouver le nombre maximal de colonnes
    max_cols = max(len(row) for row in table_rows)
    
    # S'assurer que toutes les lignes ont le même nombre de colonnes
    for row in table_rows:
        while len(row) < max_cols:
            row.append("")
    
    # Calculer les largeurs des colonnes
    col_widths = []
    for col_idx in range(max_cols):
        max_width = max(len(str(row[col_idx])) for row in table_rows)
        col_widths.append(max(max_width + 2, cell_width))
    
    # Construire le séparateur
    separator = "+" + "+".join("-" * w for w in col_widths) + "+"
    
    # Construire les lignes formatées
    lines.append(separator)
    
    for row_idx, row in enumerate(table_rows):
        formatted_cells = []
        for col_idx, cell in enumerate(row):
            formatted_cells.append(str(cell).center(col_widths[col_idx]))
        lines.append("|" + "|".join(formatted_cells) + "|")
        
        # Séparateur après l'en-tête et avant Zi
        if row_idx == 1 or row_idx == len(table_rows) - 3:
            lines.append(separator)
    
    lines.append(separator)
    
    return "\n".join(lines)


def display_solution(tableau: Tableau, num_original_vars: int) -> str:
    """
    Affiche la solution actuelle du tableau.
    
    Args:
        tableau: Tableau du simplexe
        num_original_vars: Nombre de variables originales
        
    Returns:
        Chaîne représentant la solution
    """
    lines = []
    z, _ = tableau.compute_z()
    
    lines.append("Solution actuelle:")
    
    # Variables de base
    for i, basis_idx in enumerate(tableau.basis):
        var_name = tableau.var_names[basis_idx]
        value = tableau.b[i]
        lines.append(f"  {var_name} = {format_fraction(value)}")
    
    # Variables hors base (= 0)
    non_basic = set(range(tableau.num_cols)) - set(tableau.basis)
    for j in sorted(non_basic):
        if j < num_original_vars:  # Seulement les variables originales
            var_name = tableau.var_names[j]
            lines.append(f"  {var_name} = 0")
    
    lines.append(f"\nz = {format_fraction(z)}")
    
    return "\n".join(lines)


def display_cut(cut: GomoryCut, var_names: List[str]) -> str:
    """
    Affiche une coupe de Gomory de manière détaillée.
    
    Args:
        cut: Coupe à afficher
        var_names: Noms des variables
        
    Returns:
        Chaîne représentant la coupe
    """
    lines = []
    lines.append("")
    lines.append("-" * 50)
    lines.append("COUPE DE GOMORY")
    lines.append("-" * 50)
    
    # Ligne source
    lines.append(f"Variable source: {cut.source_var} (ligne {cut.source_row})")
    lines.append(f"Partie décimale de b: {{{format_fraction(cut.fractional_rhs)}}}")
    lines.append("")
    
    # Équation de la ligne source (simplifiée)
    lines.append("Ligne du tableau:")
    terms = [f"{cut.source_var}"]
    for j, frac in enumerate(cut.fractional_parts):
        if frac != 0 and j < len(var_names):
            sign = "+" if frac > 0 else ""
            terms.append(f"{sign}({format_fraction(cut.coefficients[j])})*{var_names[j]}")
    
    # Coupe sous forme >= (forme du cours)
    lines.append("")
    lines.append("Coupe de Gomory (forme ≥):")
    geq_terms = []
    for j, frac in enumerate(cut.fractional_parts):
        if frac != 0 and j < len(var_names):
            geq_terms.append(f"({format_fraction(frac)})*{var_names[j]}")
    
    if geq_terms:
        lines.append(f"  {' + '.join(geq_terms)} ≥ {format_fraction(cut.fractional_rhs)}")
    
    # Coupe sous forme <= (pour le tableau)
    lines.append("")
    lines.append("Coupe transformée (forme ≤):")
    leq_terms = []
    for j, coef in enumerate(cut.coefficients):
        if coef != 0 and j < len(var_names):
            leq_terms.append(f"({format_fraction(coef)})*{var_names[j]}")
    
    if leq_terms:
        lines.append(f"  {' + '.join(leq_terms)} ≤ {format_fraction(cut.rhs)}")
    
    # Avec variable d'écart
    lines.append("")
    lines.append("Forme standard (avec variable d'écart):")
    std_terms = []
    for j, coef in enumerate(cut.coefficients):
        if coef != 0 and j < len(var_names):
            std_terms.append(f"({format_fraction(coef)})*{var_names[j]}")
    
    new_var = f"x{len(var_names) + 1}"
    if std_terms:
        lines.append(f"  {' + '.join(std_terms)} + {new_var} = {format_fraction(cut.rhs)}")
    
    lines.append("")
    lines.append(f"Note: {new_var} = {format_fraction(cut.rhs)} < 0")
    lines.append("      → Solution non réalisable, appliquer le dual simplexe")
    lines.append("-" * 50)
    
    return "\n".join(lines)


def display_iteration_summary(
    iteration: int,
    phase: str,
    z_value: Fraction,
    solution: List[Fraction],
    is_integer: bool
) -> str:
    """
    Affiche un résumé d'une itération.
    
    Args:
        iteration: Numéro de l'itération
        phase: Phase de l'algorithme
        z_value: Valeur de z
        solution: Solution actuelle
        is_integer: Si la solution est entière
        
    Returns:
        Chaîne représentant le résumé
    """
    lines = []
    lines.append(f"\n--- Itération {iteration} ({phase}) ---")
    lines.append(f"z = {format_fraction(z_value)}")
    
    sol_str = ", ".join(f"x{i+1}={format_fraction(v)}" for i, v in enumerate(solution))
    lines.append(f"x = ({sol_str})")
    
    if is_integer:
        lines.append("✓ Solution entière")
    else:
        lines.append("✗ Solution non entière")
    
    return "\n".join(lines)


def display_final_result(
    status: str,
    z_value: Optional[Fraction],
    solution: Optional[List[Fraction]],
    num_cuts: int,
    num_iterations: int
) -> str:
    """
    Affiche le résultat final de la résolution.
    
    Args:
        status: Statut final
        z_value: Valeur optimale
        solution: Solution optimale
        num_cuts: Nombre de coupes ajoutées
        num_iterations: Nombre d'itérations
        
    Returns:
        Chaîne représentant le résultat
    """
    lines = []
    width = 60
    
    lines.append("")
    lines.append("=" * width)
    lines.append("RÉSULTAT FINAL".center(width))
    lines.append("=" * width)
    lines.append(f"Statut: {status}")
    
    if z_value is not None:
        lines.append(f"Valeur optimale: z* = {format_fraction(z_value)}")
    
    if solution is not None:
        lines.append("Solution optimale:")
        for i, val in enumerate(solution):
            lines.append(f"  x{i+1} = {format_fraction(val)}")
    
    lines.append(f"Nombre de coupes de Gomory: {num_cuts}")
    lines.append(f"Nombre total d'itérations: {num_iterations}")
    lines.append("=" * width)
    
    return "\n".join(lines)
