# class GerenciadorDeMemoria:
#     def init_gerenciador_de_memoria(self):

# classe da Tabela de Paginas

# import tkinter
import math


class TP:
    # inicializa a Tabela de Paginas
    def __init__(self, n_entradas, tam_endereco):
        self.n_entradas = n_entradas
        self.tam_endereco = tam_endereco
        self.entradas = self.init_entradas()

    # inicializa o dicionario entradas que representa as entradas da TP
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
    def atualizar(self, n_pagina, p, m, n_quadro, GM):
        for entrada in self.entradas:
            if entrada['Presenca'] == 0:
                entrada['Presenca'] = 1
                entrada['Modificacao'] = m
                entrada['Quadro'] = n_quadro
            else:
                GM.politica_substituicao()

    # mostra o estado atual da TP
    def mostrar(self):
        for item in self.entradas:
            print(item)


class TLB:

    # inicializa a TLB
    def __init__(self, n_entradas, tam_endereco):
        self.n_entradas = n_entradas
        self.tam_endereco = tam_endereco
        self.entradas = self.init_entradas()

    # inicializa o dicionario entradas que representa as entradas da TLB
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

    # Busca nas entradas da TLB uma pagina especifica e também ve se é válida a pagina
    def buscar(self, n_pagina):
        for entrada in self.n_entradas:
            if entrada['Validade'] == 1 and entrada['Pagina'] == n_pagina:
                return self.entradas[n_pagina]['Quadro']
        return -1

    # Atualiza uma entrada da TLB
    # Prec
    def atualizar(self, n_pagina, v, p, m, n_quadro, GM):
        for entrada in self.entradas:
            if entrada['Presenca'] == 0:
                entrada['Presenca'] = 1
                entrada['Validade'] = v
                entrada['Pagina'] = n_pagina
                entrada['Presenca'] = p
                entrada['Modificacao'] = m
                entrada['nQuadro'] = n_quadro
                break
            else:
                GM.politica_substituicao(self)

    def mostrar(self):
        for item in self.entradas:
            print(item)


class GerenciadorMemoria:

    # inicializa uma entrada do GerenciadorMemoria
    def __int__(self):

     def politica_substituicao():
         return 0


class MemoriaFisica:

    # inicializa uma entrada da MemoriaFisica
    def __init__(self, n_quadros, tam_quadro):
        self.nQuadros = n_quadros
        self.tamQuadro = tam_quadro


def main():
    tam_quadro = int(input("Defina o tamanho do quadro/página:"))
    tam_end_logico = int(input("Digite o tamanho do endereço lógico:"))
    n_entrada = int(input("Digite o numero de entradas da TLB:"))
    tam_mem_fisica = int(input("Digite o tamanho da memoria fisica:"))
    tam_mem_sec = int(input("Digite o tamanho da memoria secundaria:"))

    while True:

        cond = int(input("Digite 1 para memória secundária ilimitada ou 2 para memória secundária definida: "))

        if cond == 1:
            mem_secundaria = True
            break

        elif cond == 2:
            mem_secundaria = False
            break

        else:
            print("Por favor, digite 1 ou 2.")

    n_quadro = tam_mem_fisica / tam_quadro

    # tamanho do end logico esta em bit e o tmanho da pagina que é igual ao quadro esta em byte
    n_pagina = math.pow(2, tam_end_logico) / tam_quadro * 4

    # 1 bit de presenca e 1 de modificacao
    # Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
    tam_entrada_tp = 2 + math.log(n_quadro, 2)

    # 1bit de presenca, 1 bit de modificacao e 1 bit de validade
    # mesma logica do log mas agora usada tambem para o numero de paginas
    tam_entrada_tlb = 3 + math.log(n_quadro, 2) + math.log(n_pagina, 2)

    tp = TP(n_entrada, tam_entrada_tp)
    tlb = TLB(n_entrada, tam_entrada_tlb)
    mem_fisica = MemoriaFisica(n_quadro, tam_quadro)
    GM = GerenciadorMemoria()

    while True:
        print("-------------------------------------------------")
        print("Bem vindo ao simulador de gerenciador de memoria! Digte o numero referente a opcao.")
        print("1- Adcionar entrada na TP")
        print("2- Adcionar entrada na TLB")
        print("3- Sair")
        print("-------------------------------------------------")

        opcao = input()

        if opcao == 1:
            tp.atualizar(n_entrada, tam_entrada_tp, GM)

        elif opcao == 2:
            tlb.atualizar(n_entrada, tam_entrada_tlb, GM)

        elif opcao == 3:
            break

        else:
            print("Digite um numero referente as opcoes.")


if __name__ == "__main__":
    main()
