"""
Module de définition des problèmes de programmation linéaire en nombres entiers.

Ce module fournit la classe Problem pour modéliser un PLNE.
"""

from fractions import Fraction
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .fraction_utils import to_fraction, to_fraction_list, Numeric


class Sense(Enum):
    """Sens de l'optimisation."""
    MAXIMIZE = "max"
    MINIMIZE = "min"


class ConstraintType(Enum):
    """Type de contrainte."""
    LEQ = "<="  # ≤
    GEQ = ">="  # ≥
    EQ = "="    # =


@dataclass
class Constraint:
    """
    Représente une contrainte linéaire.
    
    Attributes:
        coefficients: Coefficients des variables dans la contrainte
        constraint_type: Type de contrainte (<=, >=, =)
        rhs: Membre de droite (right-hand side)
    """
    coefficients: List[Fraction]
    constraint_type: ConstraintType
    rhs: Fraction
    
    @classmethod
    def from_tuple(cls, data: Tuple[List[Numeric], str, Numeric]) -> "Constraint":
        """
        Crée une contrainte à partir d'un tuple (coeffs, type, rhs).
        
        Args:
            data: Tuple (coefficients, type_str, rhs)
            
        Returns:
            Instance de Constraint
        """
        coeffs, type_str, rhs = data
        return cls(
            coefficients=to_fraction_list(coeffs),
            constraint_type=ConstraintType(type_str),
            rhs=to_fraction(rhs)
        )


@dataclass
class Problem:
    """
    Représente un programme linéaire en nombres entiers (PLNE).
    
    Attributes:
        objective: Coefficients de la fonction objectif
        sense: Sens de l'optimisation (max ou min)
        constraints: Liste des contraintes
        integer_vars: Indices des variables qui doivent être entières
        var_names: Noms des variables (optionnel)
        
    Example:
        >>> # max z = 6x₁ + 8x₂ + 7x₃
        >>> # s.c. 4x₁ + 6x₂ + 8x₃ ≤ 14
        >>> #      x₁ ≤ 1, x₂ ≤ 1, x₃ ≤ 1
        >>> #      x ∈ ℕ³
        >>> problem = Problem(
        ...     objective=[6, 8, 7],
        ...     sense="max",
        ...     constraints=[
        ...         ([4, 6, 8], "<=", 14),
        ...         ([1, 0, 0], "<=", 1),
        ...         ([0, 1, 0], "<=", 1),
        ...         ([0, 0, 1], "<=", 1),
        ...     ],
        ...     integer_vars=[0, 1, 2]
        ... )
    """
    objective: List[Fraction] = field(default_factory=list)
    sense: Sense = Sense.MAXIMIZE
    constraints: List[Constraint] = field(default_factory=list)
    integer_vars: List[int] = field(default_factory=list)
    var_names: Optional[List[str]] = None
    
    def __init__(
        self,
        objective: List[Numeric],
        sense: Union[str, Sense] = "max",
        constraints: Optional[List[Tuple[List[Numeric], str, Numeric]]] = None,
        integer_vars: Optional[List[int]] = None,
        var_names: Optional[List[str]] = None
    ):
        """
        Initialise un problème PLNE.
        
        Args:
            objective: Coefficients de la fonction objectif
            sense: "max" ou "min"
            constraints: Liste de tuples (coeffs, type, rhs)
            integer_vars: Indices des variables entières
            var_names: Noms des variables
        """
        self.objective = to_fraction_list(objective)
        self.sense = Sense(sense) if isinstance(sense, str) else sense
        self.constraints = []
        
        if constraints:
            for c in constraints:
                self.constraints.append(Constraint.from_tuple(c))
        
        self.integer_vars = integer_vars if integer_vars is not None else []
        
        # Générer des noms par défaut si non fournis
        n = len(objective)
        if var_names is None:
            self.var_names = [f"x{i+1}" for i in range(n)]
        else:
            self.var_names = var_names
    
    @property
    def num_variables(self) -> int:
        """Nombre de variables de décision."""
        return len(self.objective)
    
    @property
    def num_constraints(self) -> int:
        """Nombre de contraintes."""
        return len(self.constraints)
    
    def add_constraint(
        self,
        coefficients: List[Numeric],
        constraint_type: str,
        rhs: Numeric
    ) -> None:
        """
        Ajoute une contrainte au problème.
        
        Args:
            coefficients: Coefficients des variables
            constraint_type: Type de contrainte ("<=", ">=", "=")
            rhs: Membre de droite
        """
        self.constraints.append(Constraint.from_tuple((coefficients, constraint_type, rhs)))
    
    def is_integer_var(self, index: int) -> bool:
        """Vérifie si une variable doit être entière."""
        return index in self.integer_vars
    
    def get_relaxed(self) -> "Problem":
        """
        Retourne le problème relaxé (sans contraintes d'intégrité).
        
        Returns:
            Nouveau problème sans contraintes d'intégrité
        """
        return Problem(
            objective=self.objective,
            sense=self.sense,
            constraints=[(c.coefficients, c.constraint_type.value, c.rhs) 
                        for c in self.constraints],
            integer_vars=[],  # Plus de contraintes d'intégrité
            var_names=self.var_names
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du problème."""
        lines = []
        
        # Fonction objectif
        sense_str = "max" if self.sense == Sense.MAXIMIZE else "min"
        obj_terms = []
        for i, c in enumerate(self.objective):
            if c != 0:
                var = self.var_names[i] if self.var_names else f"x{i+1}"
                if c == 1:
                    term = var
                elif c == -1:
                    term = f"-{var}"
                else:
                    term = f"{c}*{var}"
                obj_terms.append(term)
        
        lines.append(f"{sense_str} z = {' + '.join(obj_terms)}")
        lines.append("sous contraintes:")
        
        # Contraintes
        for constraint in self.constraints:
            terms = []
            for i, c in enumerate(constraint.coefficients):
                if c != 0:
                    var = self.var_names[i] if self.var_names else f"x{i+1}"
                    if c == 1:
                        term = var
                    elif c == -1:
                        term = f"-{var}"
                    else:
                        term = f"{c}*{var}"
                    terms.append(term)
            
            lhs = " + ".join(terms) if terms else "0"
            lines.append(f"  {lhs} {constraint.constraint_type.value} {constraint.rhs}")
        
        # Contraintes d'intégrité
        if self.integer_vars:
            int_vars = ", ".join(self.var_names[i] for i in self.integer_vars)
            lines.append(f"  {int_vars} ∈ ℤ⁺")
        
        return "\n".join(lines)
    
    def to_latex(self) -> str:
        """
        Génère une représentation LaTeX du problème.
        
        Returns:
            Chaîne LaTeX
        """
        from .fraction_utils import format_fraction_latex
        
        lines = []
        lines.append("\\begin{aligned}")
        
        # Fonction objectif
        sense_str = "\\max" if self.sense == Sense.MAXIMIZE else "\\min"
        obj_terms = []
        for i, c in enumerate(self.objective):
            if c != 0:
                var = f"x_{{{i+1}}}"
                coef = format_fraction_latex(c)
                if coef == "1":
                    term = var
                elif coef == "-1":
                    term = f"-{var}"
                else:
                    term = f"{coef}{var}"
                obj_terms.append(term)
        
        lines.append(f"&{sense_str} \\quad z = {' + '.join(obj_terms)} \\\\")
        lines.append("&\\text{sous contraintes :} \\\\")
        
        # Contraintes
        for constraint in self.constraints:
            terms = []
            for i, c in enumerate(constraint.coefficients):
                if c != 0:
                    var = f"x_{{{i+1}}}"
                    coef = format_fraction_latex(c)
                    if coef == "1":
                        term = var
                    elif coef == "-1":
                        term = f"-{var}"
                    else:
                        term = f"{coef}{var}"
                    terms.append(term)
            
            lhs = " + ".join(terms) if terms else "0"
            type_latex = {"<=": "\\leq", ">=": "\\geq", "=": "="}
            rhs = format_fraction_latex(constraint.rhs)
            lines.append(f"&{lhs} {type_latex[constraint.constraint_type.value]} {rhs} \\\\")
        
        # Contraintes d'intégrité
        if self.integer_vars:
            vars_latex = ", ".join(f"x_{{{i+1}}}" for i in self.integer_vars)
            lines.append(f"&{vars_latex} \\in \\mathbb{{Z}}^+ \\\\")
        
        lines.append("\\end{aligned}")
        
        return "\n".join(lines)
