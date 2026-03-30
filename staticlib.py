import numpy as np
import matplotlib.pyplot as plt

'''
class Force:
    def __init__(self, magnitude, application_point,  versor):
        self.magnitude = magnitude
        self.versor = versor #versor é um vetor unitário que indica a direção da força
        self.application_point = application_point  #posição onde a força é aplicada, geralmente um nó ou coordenada específica
'''
        
class Moment:
    def __init__(self, magnitude, application_point, wise_direction):
        self.magnitude = magnitude
        self.application_point = application_point  #posição onde o momento é aplicado, geralmente um nó ou coordenada específica
        self.wise_direction = wise_direction  # Direção do momento: 1 para anti-horário, -1 para horário

class Node:
    def __init__(self, pos, liberdade):
        self.pos = pos
        self.neighbor = []  # Armazena outros objetos Node
        self.liberdade = liberdade  # tupla indicando se o nó é livre ou restrito em cada direção (x, y)

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbor:
            self.neighbor.append(neighbor)
    def __repr__(self):
        return str(self.pos)

'''
class Suport:
    def __init__(self, node, type):
        self.node = node
        self.type = type  # Ex: 'fixo', 'movel', 'engaste'
'''

class Elemento:

    def __init__(self, no_1, no_2, area_transversal, modulo_elasticidade):
        self.no_1 = no_1
        self.no_2 = no_2
        self.area_transversal = area_transversal
        self.modulo_elasticidade = modulo_elasticidade
        self.length = ((no_2.pos[0] - no_1.pos[0]) ** 2 + (no_2.pos[1] - no_1.pos[1]) ** 2) ** 0.5
        self.versor = np.array([(no_2.pos[0] - no_1.pos[0]) / self.length, (no_2.pos[1] - no_1.pos[1]) / self.length])
        self.matriz_rigidez = self.CalcularMatrizRigidez()

    def CalcularMatrizRigidez(self):
        k = (self.area_transversal * self.modulo_elasticidade) / self.length
        cos = self.versor[0]  # cos(θ)
        sen = self.versor[1]  # sen(θ)
        matriz = np.array([ [cos**2, cos*sen, -cos**2, -cos*sen],
                            [cos*sen, sen**2, -cos*sen, -sen**2],
                            [-cos**2, -cos*sen, cos**2, cos*sen],
                            [-cos*sen, -sen**2, cos*sen, sen**2]])
        nos = [self.no_1, self.no_2]
        for i in range(4):
            if nos[i//2].liberdade[i%2] == 0:  # Se o nó é restrito na direção correspondente
                matriz[i, :] = 0  # Zera a linha correspondente
                matriz[:, i] = 0  # Zera a coluna correspondente
                matriz[i, i] = 1  # Coloca um 1 na diagonal para evitar singularidade
        
        return k * matriz
        

class Structure:
    def __init__(self, elementos = []):
        self.elementos = elementos
        self.nos = []
        for elemento in elementos:
            self.nos.append(elemento.no_1)
            self.nos.append(elemento.no_2)
        self.nos = list(set(self.nos))  # Remove nós duplicados
        self.coords_nos = []
        self.coords_nos = [np.concatenate((self.coords_nos, no.pos)) for no in self.nos]
        self.nos_deformados = self.nos

        self.MatrizRigidez = self.CalcularMatrizRigidezGlobal()
    
    def CalcularMatrizRigidezGlobal(self):
        matrizes_globais = [] # Lista para armazenar as matrizes globais de cada elemento

        '''Escrever matriz do elemento como uma matriz global. Para isso,
        cada matriz de um elemento é dividida em blocos correspondentes à cada nó,
        com a matriz global sendo construída a partir desses blocos. Para a identificação
        dos blocos, é necessário identificar as coordenadas dos nós do elemento
        e mapear essas coordenadas para as posições correspondentes na matriz global.'''
        for elemento in self.elementos:
            id_nós = [self.nos.index(elemento.no_1), self.nos.index(elemento.no_2)] # identifica os índices dos nós do elemento

            coord_blocos = []
            for i in range(2):
                for j in range(2):
                    coord_blocos.append((id_nós[i], id_nós[j])) # Identifica as coordenadas dos blocos na matriz global
            
            blocos_matriz_elemento = []
            dividir_verticalmente = np.vsplit(elemento.matriz_rigidez, 2) # Divide a matriz de rigidez do elemento em blocos verticais
            for bloco in dividir_verticalmente:
                dividir_horizontalmente = np.hsplit(bloco, 2) # Divide cada bloco vertical em blocos horizontais
                blocos_matriz_elemento.extend(dividir_horizontalmente) # Armazena os blocos da matriz do elemento

            # Cria um dicionário para mapear as coordenadas dos blocos na matriz global aos blocos da matriz do elemento
            dicionario_blocos = {coordenada: bloco for coordenada, bloco in zip(coord_blocos, blocos_matriz_elemento)}

            #Cria a matriz global como uma matriz de blocos, com os blocos da matriz do elemento posicionados de acordo com as coordenadas identificadas, e os blocos vazios preenchidos com zeros
            linhas_blocos_matriz_global = []
            for i in range(len(self.nos)):
                linha_bloco_matriz_global = []
                for j in range(len(self.nos)):
                    if (i, j) in dicionario_blocos:
                        bloco_matriz_global = dicionario_blocos[(i, j)]
                    else:
                        bloco_matriz_global = np.zeros((2, 2)) # Bloco vazio para coordenadas que não correspondem a blocos do elemento
                    linha_bloco_matriz_global.append(bloco_matriz_global)
                linhas_blocos_matriz_global.append(linha_bloco_matriz_global)
            matriz_global = np.block(linhas_blocos_matriz_global) # Constrói a matriz global a partir dos blocos

            matrizes_globais.append(matriz_global)

        matriz_global_total = sum(matrizes_globais) # Soma as matrizes globais de todos os elementos para obter a matriz global total da estrutura
        return matriz_global_total

    def AplicarForcas(self, forcas): # 'forcas' é um dicionário onde as chaves são os nós e os valores são as forças aplicadas nesses nós
        vetor_forcas = []
        for no in self.nos:
            if no in forcas:
                vetor_forcas.append(forcas[no])
            else:
                vetor_forcas.append((0, 0))  # Se não houver força aplicada, considera como (0, 0)

        vetor_forcas = np.concatenate(vetor_forcas)  # Concatena as forças em um único vetor
        u = np.linalg.solve(self.MatrizRigidez, vetor_forcas)  # Resolve o sistema de equações para obter os deslocamentos

        # Atualiza as posições dos nós com base nos deslocamentos calculados
        for i, no in enumerate(self.nos_deformados):
            no.pos = (no.pos[0] + u[2*i], no.pos[1] + u[2*i + 1])
                        
    def add_edge(self, no_1, no_2):
        # Garante que os nós existem
        if no_1 not in self.nos:
            raise ValueError(f"Nó '{no_1}' não existe.")
        if no_2 not in self.nos:
            raise ValueError(f"Nó '{no_2}' não existe.")
        
        # Faz o objeto 'no_1' guardar o objeto 'no_2'
        self.nos[no_1].add_neighbor(self.nos[no_2])
        self.nos[no_2].add_neighbor(self.nos[no_1])

    def show_nodes(self):
        for valor, no in self.nos.items():
            print(f"Nó {valor} conectado a: {no.neighbor}")
    
    def show_structure(self):
        plt.figure(figsize=(4, 4))
        for valor, no in self.nos.items():
            for neighbor in no.neighbor:
                plt.plot([no.pos[0], neighbor.pos[0]], [no.pos[1], neighbor.pos[1]], 'k-')

            plt.plot(no.pos[0], no.pos[1], 'ro')  # Nó em vermelho
            plt.text(no.pos[0], no.pos[1], valor, fontsize=12, ha='right', va='bottom')  # Rótulo do nó

        for valor, force in self.forces.items():
            plt.arrow(force.application_point[0] - force.direction[0]*1.1, force.application_point[1] - force.direction[1]*1.1, force.direction[0], force.direction[1], head_width=0.1, head_length=0.1, fc='blue', ec='blue')
            plt.text(force.application_point[0] + force.direction[0]*0.1, force.application_point[1] + force.direction[1]*.1, valor, fontsize=10, ha='left', va='bottom', color='blue')
        
        # for valor, suport in self.suportes.items():
        #     if suport.type == 'fixo':
        #         ## Desenho de suporte fixo (triângulo) WIP


        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True)
        plt.show()

#  class Simulador:
#     def __init__(self, structure):
#         self.structure = structure

#     def solve(self):
#         # Implementar a lógica para resolver a estrutura usando métodos de análise estrutural
#         pass   