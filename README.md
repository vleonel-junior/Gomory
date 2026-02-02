# Gomory - Cutting Plane Method for Integer Linear Programming

[![PyPI version](https://badge.fury.io/py/gomory.svg)](https://pypi.org/project/gomory/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A pure Python implementation of the **Gomory cutting plane method** for solving **Integer Linear Programming (ILP)** problems. Designed for educational purposes with exact fractional arithmetic.

## ✨ Features

- **Pure Python** - No external solver dependencies
- **Exact arithmetic** - Uses fractions instead of floating-point numbers
- **Educational** - Step-by-step display of simplex tableaux at each iteration
- **Complete traceability** - Follow every step of the algorithm
- **Primal & Dual Simplex** - Full implementation of both methods
- **Gomory cuts generation** - Automatic cutting plane generation

## 🚀 Installation

```bash
pip install gomory
```

### From GitHub (development)

```bash
git clone https://github.com/vleonel-junior/Gomory.git
cd Gomory
pip install -e .
```

## 📋 Quick Start

```python
from gomory import Problem, GomorySolver

# Define an Integer Linear Programming problem
# max z = 6x₁ + 8x₂ + 7x₃
# subject to:
#   4x₁ + 6x₂ + 8x₃ ≤ 14
#   x₁ ≤ 1, x₂ ≤ 1, x₃ ≤ 1
#   xᵢ ∈ ℤ⁺ (integer variables)

problem = Problem(
    objective=[6, 8, 7],
    sense="max",
    constraints=[
        ([4, 6, 8], "<=", 14),
        ([1, 0, 0], "<=", 1),
        ([0, 1, 0], "<=", 1),
        ([0, 0, 1], "<=", 1),
    ],
    integer_vars=[0, 1, 2],  # indices of integer variables
    var_names=["x1", "x2", "x3"]
)

# Solve with verbose output
solver = GomorySolver(problem, verbose=True)
solution = solver.solve()

# Display solution
print(solution)
```

### Expected Output

```
Optimal integer solution found!
x1 = 0, x2 = 1, x3 = 1
z* = 15
```

## 📚 How It Works

The Gomory cutting plane method solves Integer Linear Programs through:

### 1. LP Relaxation
First, solve the linear program without integrality constraints using the primal simplex method.

### 2. Gomory Cut Generation
If the solution is not integer, generate a Gomory cut from the row with the largest fractional part.

### 3. Dual Simplex
After adding the cut, the dual simplex method restores feasibility.

### 4. Iteration
Repeat until an integer solution is found.

## 🧪 Tests

```bash
pytest tests/
```

## 📁 Project Structure

```
gomory/
├── gomory/
│   ├── __init__.py          # Package exports
│   ├── fraction_utils.py    # Fraction utilities
│   ├── problem.py           # Problem modeling
│   ├── tableau.py           # Simplex tableau
│   ├── simplex.py           # Primal simplex
│   ├── dual_simplex.py      # Dual simplex
│   ├── gomory_cut.py        # Cut generation
│   ├── solver.py            # Main solver
│   └── display.py           # Formatted display
├── tests/                   # Unit tests
├── examples/                # Usage examples
└── pyproject.toml           # Package configuration
```

## 🔗 See Also

- [Integer Linear Programming (Wikipedia)](https://en.wikipedia.org/wiki/Integer_programming)
- [Gomory Cutting Planes (Wikipedia)](https://en.wikipedia.org/wiki/Cutting-plane_method)

## 📄 License

MIT License
