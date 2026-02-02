# Gomory - Méthode des Coupes de Gomory

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Package Python pour la résolution de **Programmes Linéaires en Nombres Entiers (PLNE)** par la méthode des coupes de Gomory.

## 📖 Description

Ce package implémente la méthode des coupes de Gomory pour résoudre des problèmes d'optimisation linéaire en nombres entiers. Il respecte la méthodologie académique avec :

- **Arithmétique exacte** : utilisation exclusive de fractions (pas de nombres flottants)
- **Affichage détaillé** : tableaux du simplexe formatés à chaque itération
- **Traçabilité complète** : suivi de chaque étape de l'algorithme

## 🚀 Installation

### Depuis le dépôt GitHub

```bash
# Cloner le dépôt
git clone https://github.com/vleonel-junior/Gomory.git
cd Gomory

# Créer un environnement virtuel (recommandé)
python -m venv .venv

# Activer l'environnement virtuel
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Installer le package en mode développement
pip install -e .
```

### Installation rapide (si déjà cloné)

```bash
pip install -e .
```

La commande `pip install -e .` installe le package en mode "editable" (développement), ce qui permet de modifier le code source sans avoir à réinstaller le package.

## 📋 Utilisation

### Exemple : Problème du sac à dos

```python
from gomory import Problem, GomorySolver

# Définir le problème
# max z = 6x₁ + 8x₂ + 7x₃
# sous contraintes:
#   4x₁ + 6x₂ + 8x₃ ≤ 14
#   x₁ ≤ 1, x₂ ≤ 1, x₃ ≤ 1
#   xᵢ ∈ ℕ

problem = Problem(
    objective=[6, 8, 7],
    sense="max",
    constraints=[
        ([4, 6, 8], "<=", 14),
        ([1, 0, 0], "<=", 1),
        ([0, 1, 0], "<=", 1),
        ([0, 0, 1], "<=", 1),
    ],
    integer_vars=[0, 1, 2],  # indices des variables entières
    var_names=["x1", "x2", "x3"]
)

# Résoudre
solver = GomorySolver(problem, verbose=True)
solution = solver.solve()

# Afficher la solution
print(solution)
```

### Résultat attendu

```
Solution optimale entière trouvée !
x1 = 0, x2 = 1, x3 = 1
z* = 15
```

## 📚 Méthodologie

### 1. Résolution du programme linéaire relaxé
Le simplexe primal est d'abord appliqué au problème sans les contraintes d'intégrité.

### 2. Génération des coupes de Gomory
Si la solution n'est pas entière, une coupe de Gomory est générée à partir de la ligne ayant la plus grande partie décimale.

### 3. Application du dual simplexe
Après ajout de la coupe, l'algorithme dual du simplexe restaure la faisabilité.

### 4. Itération
Le processus se répète jusqu'à obtention d'une solution entière.

## 🧪 Tests

```bash
pytest tests/
```

## 📁 Structure du projet

```
gomory/
├── gomory/
│   ├── __init__.py          # Exports du package
│   ├── fraction_utils.py    # Utilitaires pour fractions
│   ├── problem.py           # Modélisation du problème
│   ├── tableau.py           # Tableau du simplexe
│   ├── simplex.py           # Simplexe primal
│   ├── dual_simplex.py      # Simplexe dual
│   ├── gomory_cut.py        # Génération des coupes
│   ├── solver.py            # Solveur principal
│   └── display.py           # Affichage formaté
├── tests/                   # Tests unitaires
├── examples/                # Exemples d'utilisation
└── pyproject.toml           # Configuration du package
```

## 📄 Licence

MIT License
