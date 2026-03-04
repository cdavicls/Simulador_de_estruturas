import matplotlib
matplotlib.use('TkAgg') # Força o uso do renderizador de janelas interativo
import matplotlib.pyplot as plt
import staticlib as sl


strc = sl.Structure()

strc.add_node('A', (0, 0))
strc.add_node('B', (1, 2))
strc.add_node('C', (2, 0))

strc.add_edge('A', 'B')
strc.add_edge('B', 'C')
strc.add_edge('C', 'A')

strc.add_forces('F1', 100, (1, 2), (0, -1))  # Exemplo de força aplicada no nó B

strc.add_suport('S1', 'A', 'fixo')  # Exemplo de suporte fixo no nó A

strc.show_structure()


strc.show_nodes()