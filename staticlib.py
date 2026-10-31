import numpy as np
import matplotlib.pyplot as plt


class Node:
    def __init__(self, pos, liberdade, nome=''):
        self.nome = nome
        self.pos = pos
        self.neighbor = []  # Armazena outros objetos Node
        self.liberdade = liberdade  # tupla indicando se o nó é livre ou restrito em cada direção (x, y)
        self.deslocamento = (0.0, 0.0)

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbor:
            self.neighbor.append(neighbor)
    def __repr__(self):
        return str(self.pos)


class Elemento:

    def __init__(self, no_1, no_2, area_transversal, I,  modulo_elasticidade, escoamento):

        self.no_1 = no_1
        self.no_2 = no_2
        self.length = ((no_2.pos[0] - no_1.pos[0]) ** 2 + (no_2.pos[1] - no_1.pos[1]) ** 2) ** 0.5
        self.versor = np.array([(no_2.pos[0] - no_1.pos[0]) / self.length, (no_2.pos[1] - no_1.pos[1]) / self.length])
        self.I = I
        self.area_transversal = area_transversal
        self.proj_matrix = np.array([[self.versor[0], self.versor[1], 0, 0],
                                     [0, 0, self.versor[0], self.versor[1]]])

        self.modulo_elasticidade = modulo_elasticidade
        self.k = (self.area_transversal * self.modulo_elasticidade) / self.length
        self.escoamento = escoamento
        self.K = self.k *np.array([[1, -1],
                                   [-1, 1]])
        self.carga_critica_flambagem = modulo_elasticidade*self.I*np.pi**2 / self.length**2

        self.forca_normal = 0.0
        self.tensao_normal = 0.0
        self.margem_seguranca_flambagem = 0.0
        self.margem_seguranca_escoamento = 0.0
        self.margem_seguranca = 0.0

    def aplicar_forca_normal(self, forca_normal):
        self.forca_normal = forca_normal
        self.tensao_normal = forca_normal/self.area_transversal
        if forca_normal == 0:
            self.margem_seguranca_escoamento = 1
            self.margem_seguranca_flambagem = 1
        else:
            self.margem_seguranca_escoamento = abs(self.escoamento/self.tensao_normal) - 1
            if forca_normal < 0:
                self.margem_seguranca_flambagem = abs(self.carga_critica_flambagem/self.forca_normal) - 1
            else:
                self.margem_seguranca_flambagem = 1

        self.margem_seguranca = min([self.margem_seguranca_escoamento, self.margem_seguranca_flambagem])

class Structure:

    def __init__(self, elementos = []):
        self.elementos = elementos
        self.nos = []
        for elemento in elementos:
            self.nos.append(elemento.no_1)
            self.nos.append(elemento.no_2)
        self.nos = list(set(self.nos))  # Remove nós duplicados
        self.n_elementos = len(self.elementos)
        self.n_nos = len(self.nos)
        self.id_nos = dict(zip(self.nos, [self.nos.index(no) for no in self.nos])) #Associa cada nó à sua posição na lista de nós
        self.coords_nos = []
        self.coords_nos = [np.concatenate((self.coords_nos, no.pos)) for no in self.nos]
        self.id_elementos = dict(zip(self.elementos, [self.elementos.index(elemento)]))

        self.matriz_projecao = self.espalhamento_matriz_projecao()
        self.K_local = self.espalhamento_K_local()
        self.K_sem_cc = np.zeros((2*self.n_nos, 2*self.n_nos))
        self.K_global = np.zeros((2*self.n_nos, 2*self.n_nos))
        self.espalhamento_K()

        self.forcas = np.zeros(2*self.n_nos)
        self.margem_seguranca = 0


    def espalhamento_matriz_projecao(self):
        matriz_global = np.zeros((2*self.n_elementos, 2*self.n_nos))

        for i in range(self.n_elementos):
            elemento = self.elementos[i]
            id_nos = [self.id_nos[elemento.no_1], self.id_nos[elemento.no_2]]
            blocos = np.hsplit(elemento.proj_matrix, 2)
            for j in range(2):
                ii = 2*i
                jj = 2*id_nos[j]
                np.copyto(matriz_global[ii:ii+2, jj:jj+2], blocos[j])
        return matriz_global

    def espalhamento_K_local(self):
        matriz_global = np.zeros((2*self.n_elementos, 2*self.n_elementos))
        for i in range(self.n_elementos):
            ii = 2*i
            np.copyto(matriz_global[ii:ii+2, ii:ii+2], self.elementos[i].K)
        return matriz_global

    def espalhamento_K(self):
        matriz = self.matriz_projecao.T@self.K_local@self.matriz_projecao
        np.copyto(self.K_sem_cc, matriz)
        #condicoes_de_contorno
        for i in range(self.n_nos):
            no = self.nos[i]
            ii = 2*i
            if no.liberdade[0] == 0:
                matriz[:, ii] = 0
                matriz[ii, :] = 0
                matriz[ii, ii] = 1
            if no.liberdade[1] == 0:
                matriz[:, ii+1] = 0
                matriz[ii+1, :] = 0
                matriz[ii+1, ii+1] = 1
        np.copyto(self.K_global, matriz)
    

    def aplicar_forcas(self, forcas): # 'forcas' é um dicionário onde as chaves são os nós e os valores são as forças aplicadas nesses nós
        margens_seguranca = np.zeros(self.n_elementos)
        for i in range(self.n_nos):
            no = self.nos[i]
            if no in forcas:
                if no.liberdade[0] == 1:
                    self.forcas[2*i] = forcas[no][0]
                if no.liberdade[1] == 1:
                    self.forcas[2*i+1]+= forcas[no][1]


        u = np.linalg.solve(self.K_global, self.forcas) # Resolve o sistema de equações para obter os deslocamentos
        self.vetor_deslocamentos = u

        for i, no in enumerate(self.nos):
            no.deslocamento = (u[2*i], u[2*i + 1])
        forcas_elementos = self.K_local@self.matriz_projecao@u
        for i, elemento in enumerate(self.elementos):
            f_i, f_j = forcas_elementos[2*i], forcas_elementos[2*i + 1]
            elemento.aplicar_forca_normal((f_j - f_i) / 2)
            margens_seguranca[i] = elemento.margem_seguranca
        self.margem_seguranca = min(margens_seguranca)

    def show_structure(self, deformada = 0):
        plt.figure(figsize=(4, 4))

        d = deformada

        for elemento in self.elementos:
            nos_barra = [elemento.no_1, elemento.no_2]
            x_nos_barra = [no.pos[0] + d*no.deslocamento[0] for no in nos_barra]
            y_nos_barra = [no.pos[1] + d*no.deslocamento[1] for no in nos_barra]

            plt.plot(x_nos_barra, y_nos_barra, 'k-', linewidth=5)

        for no in self.nos:
            if no.liberdade == (0, 0):
                simbolo = 's'
            else:
                simbolo = 'o'
            x_no = no.pos[0] + d*no.deslocamento[0]
            y_no = no.pos[1] + d*no.deslocamento[1]
            plt.plot(x_no, y_no, 'r'+simbolo, markersize=20)

        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True)
        return