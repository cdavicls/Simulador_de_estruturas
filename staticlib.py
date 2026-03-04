import numpy as np
import matplotlib.pyplot as plt

class Force:
    def __init__(self, magnitude, application_point,  versor):
        self.magnitude = magnitude
        self.direction = versor #versor é um vetor unitário que indica a direção da força
        self.application_point = application_point  #posição onde a força é aplicada, geralmente um nó ou coordenada específica

class Moment:
    def __init__(self, magnitude, application_point, wise_direction):
        self.magnitude = magnitude
        self.application_point = application_point  #posição onde o momento é aplicado, geralmente um nó ou coordenada específica
        self.wise_direction = wise_direction  # Direção do momento: 1 para anti-horário, -1 para horário

class Node:
    def __init__(self, pos):
        self.pos = pos
        self.neighbor = []  # Armazena outros objetos Node

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbor:
            self.neighbor.append(neighbor)
    def __repr__(self):
        return str(self.pos)

class Suport:
    def __init__(self, node, type):
        self.node = node
        self.type = type  # Ex: 'fixo', 'movel', 'engaste'

class Structure:
    def __init__(self):
        self.nos = {}  # Dicionário para gerenciar os nós
        self.forces = {}  # Dicionário para armazenar forças aplicadas aos nós
        self.suportes = {}  # Dicionário para armazenar suportes
        self.momentums = {}  # Dicionário para armazenar momentos aplicados aos nós

    def add_node(self, name , pos):
        if name not in self.nos:
            self.nos[name] = Node(pos)

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

    def add_forces(self, name, valor, application_point, versor):
        if name not in self.forces:
            self.forces[name] = Force(valor, application_point, versor)

    def add_suport(self, name, node_name, type):
        if node_name not in self.nos:
            raise ValueError(f"Nó '{node_name}' não existe.")
        if node_name in self.suportes:
            raise ValueError(f"Nó '{node_name}' já possui um suporte.")
        if name not in self.suportes:
            self.suportes[name] = Suport(self.nos[node_name], type)
            if type == 'fixo':
                self.forces["Fx_" + node_name] = Force(None, self.nos[node_name].pos, (1, 0))  # Exemplo de força para suporte fixo
                self.forces["Fy_" + node_name] = Force(None, self.nos[node_name].pos, (0, 1))  # Exemplo de força para suporte fixo
            elif type == 'movel':
                self.forces["Fx_" + node_name] = Force(None, self.nos[node_name].pos, (0, 1))  # Exemplo de força para suporte móvel
            elif type == 'engaste':
                self.forces["Fx_" + node_name] = Force(None, self.nos[node_name].pos, (1, 0))  # Exemplo de força para suporte de engaste
                self.forces["Fy_" + node_name] = Force(None, self.nos[node_name].pos, (0, 1))  # Exemplo de força para suporte de engaste
                self.momentums["M_" + node_name] = Moment(None, self.nos[node_name].pos, 1)  # Exemplo de momento para suporte de engaste

    def distance_between_nodes(self, no_1, no_2):
        if no_1 not in self.nos:
            raise ValueError(f"Nó '{no_1}' não existe.")
        if no_2 not in self.nos:
            raise ValueError(f"Nó '{no_2}' não existe.")
        pos1 = self.nos[no_1].pos
        pos2 = self.nos[no_2].pos
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    def calc_versor_between_nodes(self, no_1, no_2):
        if no_1 not in self.nos:
            raise ValueError(f"Nó '{no_1}' não existe.")
        if no_2 not in self.nos:
            raise ValueError(f"Nó '{no_2}' não existe.")
        pos1 = self.nos[no_1].pos
        pos2 = self.nos[no_2].pos
        distance = self.distance_between_nodes(no_1, no_2)
        if distance == 0:
            raise ValueError("Os nós estão na mesma posição, não é possível calcular o versor.")
        versor = ((pos2[0] - pos1[0]) / distance, (pos2[1] - pos1[1]) / distance)
        return versor
    
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
