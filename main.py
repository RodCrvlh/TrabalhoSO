# class GerenciadorDeMemoria:
#     def init_gerenciador_de_memoria(self):

# classe da Tabela de Paginas

# import tkinter
import math

# Estrutura ue mantem as paginas que não estão na memoria fisica


class MemoriaSecundaria:

    def __init__(self, tam_mem_sec, tam_pagina):
        self.tam_mem_sec = tam_mem_sec
        self.tam_pagina = tam_pagina
        self.dados = self.init_dados()

    def init_dados(self):
        dados = []
        for _ in range(self.tam_mem_sec):
            dado = {
                'Conteudo': [None]*self.tam_pagina,
                'Processo': None,  # qual processo essa pagina pertence
                'Pagina': None     # numero da pagina dentro do processo
            }
            dados.append(dado)
        return dados

    def liberar_processo(self, id_processo):
        for i, dado in enumerate(self.dados):
            if dado['Processo'] == id_processo:
                self.dados[i] = {
                    'Conteudo': [None]*self.tam_pagina,
                    'Processo': None,
                    'Pagina': None
                }

    def carregar(self, end_fisico):
        n_pagina = end_fisico//self.tam_pagina
        return self.dados[n_pagina]

    def salvar(self, id_processo, n_paginas):
        i = 0   # Numero da pagina dentro do processo
        for idx, dado in enumerate(self.dados):
            if dado['Processo'] is None:
                self.dados[idx] = {
                    'Conteudo': [None] * self.tam_pagina,
                    'Processo': id_processo,
                    'Pagina': i
                }
                i += 1
                n_paginas -= 1

        if n_paginas == 0:
            return True

        print("Espaço insuficiente na Memmoria Secundaria ")
        return False
        # n_pagina = end_fisico//self.tam_pagina
        # self.dados[n_pagina] = {
        #     'Conteudo': conteudo,
        #     'Processo': processo, #qual processo essa pagina pertence
        #     'Pagina': pagina      #numero da pagina dentro do processo
        # }

    def mostrar(self):
        print("-------------------------------")
        print("Memoria Secundaria")

        for i, dado in self.dados:
            if dado['Pagina'] is None:
                print(f"Espaço{i}: Livre")
            else:
                print(f"Espaço {i}: Pagina {dado['Pagina']}, Processo {dado['Processo']}, Conteudo:{dado['Conteudo']}")

        print("--------------------------------")


# Estrutura que mantem os dados e quadros amarzenados
class MemoriaPrincipal:

    # inicializa uma entrada da MemoriaFisica
    def __init__(self, n_quadros, tam_quadro):
        self.n_quadros = n_quadros
        self.tam_quadro = tam_quadro
        self.quadros = self.init_quadros()

    def init_quadros(self):
        quadros = []
        for _ in range(self.n_quadros):
            quadro = {
                'Dados': [None]*self.tam_quadro,
                'Processo': None,
                'Pagina': None
            }
            quadros.append(quadro)
        return quadros

    def ler(self, end_fisico):
        id_quadro = end_fisico//self.tam_quadro
        offset = end_fisico % self.tam_quadro

        return self.quadros[id_quadro]['Dados'][offset]

    def escrever(self, end_fisico, dado):
        id_quadro = end_fisico // self.tam_quadro
        offset = end_fisico % self.tam_quadro

        if id_quadro >= self.n_quadros:
            print("Endereço invalido")

        self.quadros[id_quadro]['Dados'][offset] = dado

    def alocar_quadro(self, processo, pagina):

        for i, quadro in enumerate(self.quadros):
            if quadro['Pagina'] is None:
                quadro['Pagina'] = pagina
                quadro['Processo'] = processo
                quadro['Dados'] = [None] * self.tam_quadro
                return i
        return -1

    def liberar_quadro(self, id_quadro):

        if id_quadro >= self.n_quadros:
            print("Quadro inexistente")
            return

        self.quadros[id_quadro] = {
            'Dados': [None] * self.tam_quadro,
            'Processo': None,
            'Pagina': None
        }

    def mostrar(self):
        print("Memoria Fisica:")
        print("------------------------------------")
        for i, quadro in self.quadros:
            if quadro is None:
                print(f"Quadro {i}: Livre")
            else:
                print(f"Quadro {i}: Processo{quadro['Processo']}, Pagina:{quadro['Pagina']}, Dados:{quadro['Dados']}")
        print("------------------------------------")


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
                'Quadro': None,
                'Tempo': 0
                # O tempo serve para politica LRU, significa quantas buscas foram feitas sem ele ser acessado
            }
            entradas.append(entrada)
        return entradas

    # busca na TP em que quadro uma pagina esta amarzenada
    def buscar(self, n_pagina):
        for entrada in self.entradas:
            entrada['Tempo'] += 1
        if self.entradas[n_pagina]['Presenca'] == 1:
            return self.entradas[n_pagina]['Quadro']  # pagina encontrada
        else:
            return -1

    # atualiza uma entrada da TP
    def atualizar(self, n_quadro):
        for entrada in self.entradas:
            if entrada['Presenca'] == 0:
                entrada['Presenca'] = 1
                entrada['Modificacao'] = 0
                entrada['Quadro'] = n_quadro
                entrada['Tempo'] = 0

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
                'Quadro': None,
                'Tempo': 0
            }
            entradas.append(entrada)
        return entradas

    # Busca nas entradas da TLB uma pagina especifica e também ve se é válida a pagina
    def buscar(self, n_pagina, n_quadro):
        for entrada in self.entradas:
            if entrada['Validade'] == 1 and entrada['Quadro'] == n_quadro:
                return self.entradas[n_pagina]['Quadro']

        return -1

    # Atualiza uma entrada da TLB
    # Prec
    def atualizar(self, n_pagina, v, p, m, n_quadro):
        for entrada in self.entradas:
            if entrada['Presenca'] == 0:
                entrada['Presenca'] = 1
                entrada['Validade'] = v
                entrada['Pagina'] = n_pagina
                entrada['Presenca'] = p
                entrada['Modificacao'] = m
                entrada['Quadro'] = n_quadro
                entrada['Tempo'] = 0
                break

    def mostrar(self):
        for item in self.entradas:
            print(item)


class GerenciadorMemoria:

    # inicializa uma entrada do GerenciadorMemoria
    def __init__(self, tlb, mem_principal, mem_sec):
        self.mp = mem_principal
        self.ms = mem_sec
        self.tlb = tlb
        self.processos = []
        self.politica_sub = None

    def traduzir_endereco(self, n_quadro, end_logico):
        # n_pagina = end_logico / self.mp.self.tam_quadro
        offset = end_logico % self.mp.tam_quadro
        end_fisico = (n_quadro * self.mp.tam_quadro) + offset
        return end_fisico

    def criar_processo(self, n_entradas_tp, id_processo, tam_imagem):

        n_paginas = tam_imagem/self.mp.tam_quadro

        # 1 bit de presenca e 1 de modificacao
        # Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
        tam_entrada_tp = 2 + math.log(self.mp.n_quadros, 2)

        processo = {
            'Id': id_processo,
            'TP': TP(n_entradas_tp, tam_entrada_tp)
        }
        self.processos.append(processo)
        self.ms.salvar(len(self.processos), n_paginas)

    # Primeiro precisamos liberar as paginas presentes na MP, ou seja, os que estão na TP e depois na MS
    def terminar_processo(self, id_processo):
        self.ms.liberar_processo(id_processo)
        for i, processo in enumerate(self.processos):
            if processo['Id'] == id_processo:
                tp = processo['TP']
                for entrada in tp.entradas:
                    self.mp.liberar_quadro(entrada['Quadro'])
                break

    def leitura_memoria(self, end_logico):
        end_fisico = self.traduzir_endereco(end_logico)
        if self.tlb.buscar(end_fisico) == -1:
            print()

    # @staticmethod
    # def lru(entradas):
    #
    #     maior_tempo = 0
    #     for entrada in entradas:
    #         if entrada['Tempo'] > maior_tempo:
    #             maior_tempo = entrada['Tempo']
    #
    #     for entrada in entradas:
    #         if entrada['Tempo'] == maior_tempo:
    #             entrada['Presenca'] = 0
    #
    # @staticmethod
    # def relogio(entradas):
    #     print("a")
    #
    # @staticmethod
    # def politica_substituicao(entradas):
    #     while True:
    #         print("Escolha 1 para LRU e 2 para Relógio")
    #         op = int(input())
    #         if op == 1:
    #             return GerenciadorMemoria.lru(entradas)
    #         elif op == 2:
    #             return GerenciadorMemoria.relogio(entradas)
    #         else:
    #             print("Digite as opções 1 ou 2!")


def main():
    tam_quadro = int(input("Defina o tamanho do quadro/página:"))
    tam_end_logico = int(input("Digite o tamanho do endereço lógico:"))
    n_entrada_tp = int(input("Digite o numero de entradas da TP"))
    n_entrada_tlb = int(input("Digite o numero de entradas da TLB:"))
    tam_mem_fisica = int(input("Digite o tamanho da memoria fisica:"))
    tam_mem_sec = int(input("Digite o tamanho da memoria secundaria:"))

    n_quadro = tam_mem_fisica // tam_quadro

    # tamanho do end logico esta em bit e o tmanho da pagina que é igual ao quadro esta em byte
    n_pagina = math.pow(2, tam_end_logico) // tam_quadro * 4

    # 1bit de presenca, 1 bit de modificacao e 1 bit de validade
    # mesma logica do log mas agora usada tambem para o numero de paginas
    tam_entrada_tlb = 3 + math.log(n_quadro, 2) + math.log(n_pagina, 2)

    tlb = TLB(n_entrada_tlb, tam_entrada_tlb)
    mem_principal = MemoriaPrincipal(n_quadro, tam_quadro)
    mem_sec = MemoriaSecundaria(tam_mem_sec, tam_quadro)
    gm = GerenciadorMemoria(tlb, mem_principal, mem_sec)

    while True:
        print("-------------------------------------------------")
        print("Bem vindo ao simulador de Gerenciador de Memoria! Digte o numero referente a opcao==.")
        print("P - intrução a ser executada pela CPU (sem ser leitura ou escrita")
        print("I - instrução de I/O")
        print("C - criação (submissão de processos")
        print("R - pedido de leitura executado pela CPU em um endereço lógico")
        print("W - pedido de escrita executado pela CPU em um endereço lógico de um valor")
        print("T - terminação processo")
        print("-------------------------------------------------")

        opcao = input()

        if opcao == 'P':
            print("Opcao não implementada ainda")

        elif opcao == 'I':
            print("Opcao não implementada ainda")

        elif opcao == 'C':
            tamanho = int(input("Digite o tamanho do processo"))
            id_processo = int(input("Digite o id do processo"))
            gm.criar_processo(n_entrada_tp, id_processo, tamanho)

        elif opcao == 'R':
            print("Opcao não implementada ainda")

        elif opcao == 'W':
            print("Opcao não implementada ainda")

        elif opcao == 'T':
            id_processo = int(input("Digite o id do processo"))
            gm.terminar_processo(id_processo)

        else:
            print("Digite um numero referente as opcoes.")


if __name__ == "__main__":
    main()
