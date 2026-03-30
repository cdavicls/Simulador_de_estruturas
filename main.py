import matplotlib
matplotlib.use('TkAgg') # Força o uso do renderizador de janelas interativo
import matplotlib.pyplot as plt
import staticlib as sl
import numpy as np

nos = []
nos.append(sl.Node(np.array([0, 0]), (0, 0)))
nos.append(sl.Node(np.array([1, 1]), (0, 0)))
nos.append(sl.Node(np.array([1, 0]), (1, 1)))

barras = []
barras.append(sl.Elemento(nos[0], nos[2], 1, 1))
barras.append(sl.Elemento(nos[1], nos[2], 1, 1))

for barra in barras:
    print(barra.matriz_rigidez)
    print()

strc = sl.Structure(barras)

print()
print(strc.MatrizRigidez)
