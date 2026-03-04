# Static Simulator (Simulador de Estática)

This project is an educational tool designed to simulate and analyze static structures. It serves as a practical application of numerical methods and a study aid for engineering students.

## Motivation

The intention of this project is to improve Python programming skills and create free software to be used by students of **Mechatronics Engineering at EESC-USP** (University of São Paulo, São Carlos School of Engineering). It allows students to study and verify simple statics questions, bridging the gap between theory and numerical practice.

## Features

*   **Structure Definition**: Create nodes and connect them with edges to form trusses or frames.
*   **Load Application**: Apply forces (vectors) and moments to specific points on the structure.
*   **Support Types**: Define boundary conditions with supports such as:
    *   Fixed (Fixo)
    *   Mobile (Móvel)
    *   Rigid/Cantilever (Engaste)
*   **Visualization**: Graphical representation of the structure, forces, and nodes using `matplotlib`.

## Requirements

*   Python 3
*   `numpy`
*   `matplotlib`

## Usage Example

```python
import staticlib as sl

strc = sl.Structure()

strc.add_node('A', (0, 0))
strc.add_node('B', (1, 2))
strc.add_node('C', (2, 0))

strc.add_edge('A', 'B')
strc.add_edge('B', 'C')
strc.add_edge('C', 'A')

strc.add_forces('F1', 100, (1, 2), (0, -1))

strc.add_suport('S1', 'A', 'fixo')

strc.show_structure()
```