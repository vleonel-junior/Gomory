"""
Utilitaires pour la manipulation de fractions.

Ce module fournit des fonctions pour travailler avec des fractions
de manière à respecter l'arithmétique exacte sans utiliser de floats.
"""

from fractions import Fraction
from typing import Union, List

# Type alias pour les valeurs numériques acceptées
Numeric = Union[int, float, Fraction, str]


def to_fraction(value: Numeric) -> Fraction:
    """
    Convertit une valeur en Fraction.
    
    Args:
        value: Valeur à convertir (int, float, str ou Fraction)
        
    Returns:
        Fraction correspondante
        
    Examples:
        >>> to_fraction(3)
        Fraction(3, 1)
        >>> to_fraction("1/2")
        Fraction(1, 2)
        >>> to_fraction(0.5)
        Fraction(1, 2)
    """
    if isinstance(value, Fraction):
        return value
    elif isinstance(value, int):
        return Fraction(value)
    elif isinstance(value, float):
        return Fraction(value).limit_denominator(10000)
    elif isinstance(value, str):
        return Fraction(value)
    else:
        raise TypeError(f"Cannot convert {type(value)} to Fraction")


def floor(x: Fraction) -> int:
    """
    Calcule la partie entière (floor) d'une fraction.
    
    La partie entière ⌊x⌋ est le plus grand entier inférieur ou égal à x.
    
    Args:
        x: Fraction dont on veut la partie entière
        
    Returns:
        Le plus grand entier ≤ x
        
    Examples:
        >>> floor(Fraction(7, 2))
        3
        >>> floor(Fraction(-3, 2))
        -2
        >>> floor(Fraction(4, 1))
        4
    """
    if x >= 0:
        return int(x.numerator // x.denominator)
    else:
        # Pour les négatifs, on doit arrondir vers -∞
        q, r = divmod(x.numerator, x.denominator)
        return int(q) if r == 0 else int(q)


def fractional_part(x: Fraction) -> Fraction:
    """
    Calcule la partie décimale (fractionnaire) d'une fraction.
    
    La partie décimale {x} est définie comme x - ⌊x⌋.
    Elle est toujours dans l'intervalle [0, 1).
    
    Args:
        x: Fraction dont on veut la partie décimale
        
    Returns:
        Partie décimale de x (toujours ≥ 0)
        
    Examples:
        >>> fractional_part(Fraction(7, 2))
        Fraction(1, 2)
        >>> fractional_part(Fraction(-3, 2))
        Fraction(1, 2)
        >>> fractional_part(Fraction(4, 1))
        Fraction(0, 1)
    """
    return x - floor(x)


def is_integer(x: Fraction) -> bool:
    """
    Vérifie si une fraction est un entier.
    
    Args:
        x: Fraction à vérifier
        
    Returns:
        True si x est un entier, False sinon
        
    Examples:
        >>> is_integer(Fraction(4, 1))
        True
        >>> is_integer(Fraction(4, 2))
        True
        >>> is_integer(Fraction(3, 2))
        False
    """
    return x.denominator == 1 or x.numerator % x.denominator == 0


def format_fraction(x: Fraction, always_show_sign: bool = False) -> str:
    """
    Formate une fraction pour l'affichage.
    
    Args:
        x: Fraction à formater
        always_show_sign: Si True, affiche toujours le signe (même +)
        
    Returns:
        Chaîne représentant la fraction
        
    Examples:
        >>> format_fraction(Fraction(3, 2))
        '3/2'
        >>> format_fraction(Fraction(4, 1))
        '4'
        >>> format_fraction(Fraction(-1, 2))
        '-1/2'
    """
    sign = ""
    if always_show_sign and x >= 0:
        sign = "+"
    
    if x.denominator == 1:
        return f"{sign}{x.numerator}"
    else:
        return f"{sign}{x.numerator}/{x.denominator}"


def format_fraction_latex(x: Fraction) -> str:
    """
    Formate une fraction en notation LaTeX.
    
    Args:
        x: Fraction à formater
        
    Returns:
        Chaîne LaTeX représentant la fraction
        
    Examples:
        >>> format_fraction_latex(Fraction(3, 2))
        '\\frac{3}{2}'
        >>> format_fraction_latex(Fraction(4, 1))
        '4'
    """
    if x.denominator == 1:
        return str(x.numerator)
    else:
        sign = "-" if x < 0 else ""
        return f"{sign}\\frac{{{abs(x.numerator)}}}{{{x.denominator}}}"


def to_fraction_list(values: List[Numeric]) -> List[Fraction]:
    """
    Convertit une liste de valeurs en liste de fractions.
    
    Args:
        values: Liste de valeurs à convertir
        
    Returns:
        Liste de fractions
    """
    return [to_fraction(v) for v in values]


def gcd_list(fractions: List[Fraction]) -> Fraction:
    """
    Calcule le PGCD d'une liste de fractions.
    
    Args:
        fractions: Liste de fractions
        
    Returns:
        PGCD de toutes les fractions
    """
    from math import gcd
    from functools import reduce
    
    if not fractions:
        return Fraction(1)
    
    # Convertir en fractions
    fracs = [to_fraction(f) for f in fractions if f != 0]
    
    if not fracs:
        return Fraction(1)
    
    # PGCD des numérateurs
    nums = [abs(f.numerator) for f in fracs]
    gcd_num = reduce(gcd, nums)
    
    # PPCM des dénominateurs
    def lcm(a, b):
        return abs(a * b) // gcd(a, b)
    
    denoms = [f.denominator for f in fracs]
    lcm_denom = reduce(lcm, denoms)
    
    return Fraction(gcd_num, lcm_denom)
