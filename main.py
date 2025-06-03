# class GerenciadorDeMemoria:
#     def init_gerenciador_de_memoria(self):

# classe da Tabela de Paginas

import tkinter
import math


class TP:
    # inicializa a Tabela de Paginas
    def __init__(self, n_entradas, tam_endereco):
        self.n_entradas = n_entradas
        self.tam_endereco = tam_endereco
        self.entradas = self.init_entradas()

    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Presenca':  0,
                'Modificacao': 0,
                'Quadro': None
            }
            entradas.append(entrada)
        return entradas

    # busca na TP em que quadro uma pagina esta amarzenada
    def buscar(self, n_pagina):
        if self.entradas[n_pagina]['Presenca'] == 1:
            return self.entradas[n_pagina]['Quadro']  # pagina encontrada
        else:
            return -1  # nao acha a pagina e ativa a Politica de Substituicao

    # atualiza uma entrada da TP
    def atualizar(self, n_pagina, p, m, n_quadro):
        self.entradas[n_pagina]['Presenca'] = p
        self.entradas[n_pagina]['Modificacao'] = m
        self.entradas[n_pagina]['Quadro'] = n_quadro

    def mostrar(self):
        for item in self.entradas:
            print(item)


class TLB:

    # inicializa a TLB
    def __init__(self, n_entradas, tam_endereco):
        self.n_entradas = n_entradas
        self.tam_endereco = tam_endereco
        self.entradas = self.init_entradas()


    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Validade': 0,
                'Pagina': None,
                'Presenca': 0,
                'Modificacao': 0,
                'Quadro': None
            }
            entradas.append(entrada)
        return entradas

    def buscar(self, n_pagina):
        for _ in range(self.n_entradas):
            if self.entradas['Pagina'] == n_pagina:
                return self.entradas['Quadro']
        return -1

    def atualizar(self, n_pagina_antiga, n_pagina_nova, v, p, m, n_quadro):
        i = 0
        while i < self.n_entradas:
            if self.entradas['Pagina'] == n_pagina_antiga:
                self.entradas[n_pagina_antiga]['Validade'] = v
                self.entradas[n_pagina_antiga]['Pagina'] = n_pagina_nova
                self.entradas[n_pagina_antiga]['Presenca'] = p
                self.entradas[n_pagina_antiga]['Modificacao'] = m
                self.entradas[n_pagina_antiga]['nQuadro'] = n_quadro
            else:
                i = i + 1

    def mostrar(self):
        for item in self.entradas:
            print(item)



class MemoriaFisica:

    # inicializa uma entrada da MemoriaFisica
    def __init__(self, n_quadros, tam_quadro):
        self.nQuadros = n_quadros
        self.tamQuadro = tam_quadro


def main():
    n_quadro = int(input("Defina o numero de quadros:"))
    n_pagina = int(input("Defina o numero de paginas"))
    tam_quadro = (input("Defina o tamanho do quadro/página:"))
    tam_end_logico = int(input("Digite o tamanho do endereço lógico:"))
    n_entrada = int(input("Digite o numero de entradas da TLB:"))

    cond = 0

    while cond != 1 or cond != 2:
        try:
            cond = int(
                input("Digite 1 para memória secundária ilimitada ou 2 para memória secundária definida: "))
        except ValueError:
            print("Por favor, digite um número válido (1 ou 2).")

    mem_secundaria = False

    if cond == 1:
        mem_secundaria = True
    elif cond == 2:
        mem_secundaria = False

    # 1 bit de presenca e 1 de modificacao
    # Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
    tam_entrada_tp = 2 + math.log(n_quadro, 2)
    # 1bit de presenca, 1 bit de modificacao e 1 bit de validade
    # mesma logica do log mas agora usada tambem para o numero de paginas
    tam_entrada_tlb = 3 + math.log(n_quadro, 2)+ math.log(n_pagina, 2)
    tp = TP(n_entrada, tam_entrada_tp)
    tlb = TLB(n_entrada, tam_entrada_tlb)
    mem_fisica = MemoriaFisica(n_quadro, tam_quadro)


if __name__ == "__main__":
    main()
