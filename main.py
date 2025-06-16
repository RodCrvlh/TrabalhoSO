# class GerenciadorDeMemoria:
#     def init_gerenciador_de_memoria(self):

# classe da Tabela de Paginas

# import tkinter
import math
import copy
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Estrutura que mantem as paginas que não estão na memoria principal


class MemoriaSecundaria:

    def __init__(self, tam_ms, tam_pagina):
        self.tam_ms = tam_ms
        self.tam_pg = tam_pagina
        self.dados = self.init_dados()

    def init_dados(self):
        dados = []
        tam_espaco = self.tam_ms//self.tam_pg
        for _ in range(tam_espaco):
            dado = {
                'Conteudo': [""] * self.tam_pg,
                'Processo': -1,  # qual processo essa pagina pertence
                'Pagina': -1     # numero da pagina dentro do processo
            }
            dados.append(dado)
        return dados

    def liberar_processo(self, id_processo):
        for i, dado in enumerate(self.dados):
            if dado['Processo'] == id_processo:
                self.dados[i] = {
                    'Conteudo': [""]*self.tam_pg,
                    'Processo': -1,
                    'Pagina': -1
                }

    def carregar(self, id_processo, n_pagina):
        for i, dado in enumerate(self.dados):
            if int(dado['Processo']) == id_processo and dado['Pagina'] == n_pagina:
                novo_quadro = copy.deepcopy(dado)  # cria uma cópia do dado que não referencia o seu endereço original
                self.dados[i]['Conteudo'] = [""] * self.tam_pg
                self.dados[i]['Processo'] = -1
                self.dados[i]['Pagina'] = -1
                return novo_quadro

        print(f"Pagina {n_pagina} do processo {id_processo} não está na Memória Secundária")
        return None

    def salvar(self, id_processo, n_paginas, conteudo):

        for idx, dado in enumerate(self.dados):
            if dado['Processo'] == -1:
                self.dados[idx] = {
                    'Conteudo': conteudo,
                    'Processo': id_processo,
                    'Pagina': idx
                }
                n_paginas -= 1

            if n_paginas == 0:
                return True

        print(n_paginas)
        print("Espaço insuficiente na Memoria Secundaria ")
        return False

    def mostrar(self):
        print("-------------------------------")
        print("Memoria Secundaria")

        for i, dado in enumerate(self.dados):
            if dado['Pagina'] == -1:
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
                'Conteudo': [""] * self.tam_quadro,
                'Processo': -1,
                'Pagina': -1
            }
            quadros.append(quadro)
        return quadros

    def esta_cheio(self):
        for i in range(self.n_quadros):
            if self.quadros[i]['Processo'] == -1:
                return False

        return True

    def ler(self, n_quadro):
        return self.quadros[n_quadro]

    def escrever(self, n_quadro, offset, conteudo):

        if n_quadro >= self.n_quadros:
            print("Endereço invalido")
            return None

        self.quadros[n_quadro]['Conteudo'][offset] = conteudo

    def alocar_quadro(self, processo, pagina, conteudo):

        for i, quadro in enumerate(self.quadros):
            if quadro['Pagina'] == -1:
                quadro['Pagina'] = pagina
                quadro['Processo'] = processo
                quadro['Conteudo'] = conteudo
                print(i)
                return i
        return -1

    def liberar_quadro(self, id_quadro):

        if id_quadro >= self.n_quadros:
            print("Quadro inexistente")
            return

        self.quadros[id_quadro] = {
            'Conteudo': [""] * self.tam_quadro,
            'Processo': -1,
            'Pagina': -1
        }

    def mostrar(self):
        print("Memoria Principal:")
        print("------------------------------------")
        for i, quadro in enumerate(self.quadros):
            if quadro['Processo'] == -1:
                print(f"Quadro {i}: Livre")
            else:
                print(f"Quadro {i}: Processo{quadro['Processo']}, Pagina:{quadro['Pagina']}, "
                      f"Conteudo:{quadro['Conteudo']}")
        print("------------------------------------")


class TP:
    # inicializa a Tabela de Paginas
    def __init__(self, n_entradas):
        self.n_entradas = n_entradas
        self.entradas = self.init_entradas()
        self.ponteiro_relogio = 0

    # inicializa o dicionario entradas que representa as entradas da TP
    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Presenca':  0,
                'Modificacao': 0,
                'Quadro': -1,
                'Tempo': 0,
                'Referencia': 0
                # O tempo serve para politica LRU, significa quantas buscas foram feitas sem ele ser acessado
            }
            entradas.append(entrada)
        return entradas

    def aumentar_tempo(self, n_pagina):
        print(f"pg:{n_pagina}")
        print(f"n_entradas:{self.n_entradas}")
        for i in range(self.n_entradas):
            if i != n_pagina and self.entradas[i]['Quadro'] != -1:
                print(self.entradas[i]['Tempo'])
                self.entradas[i]['Tempo'] += 1

    # busca na TP em que quadro uma pagina esta amarzenada
    def buscar(self, n_pagina, mp):

        if self.entradas[n_pagina]['Presenca'] == 1:  # Achou a pagina na TP
            self.entradas[n_pagina]['Tempo'] = 0
            self.entradas[n_pagina]['Referencia'] = 1
            self.aumentar_tempo(n_pagina)
            return self.entradas[n_pagina]['Quadro']

        elif self.entradas[n_pagina]['Quadro'] == -1:  # Não achou a pagina na TP

            if not mp.esta_cheio():  # Verifica que é possível adicionar a página na TP
                self.aumentar_tempo(n_pagina)
                return -2

            else:  # Verifica que não é possível adicionar a página na TP
                self.aumentar_tempo(n_pagina)
                return -1

    def retirar_presenca(self, tempo):
        for entrada in self.entradas:
            if entrada['Tempo'] == tempo:
                entrada['Presenca'] = 0
                break

    # atualiza uma entrada da TP
    def atualizar(self, p, m, n_quadro, n_pagina):
        self.entradas[n_pagina]['Presenca'] = p
        self.entradas[n_pagina]['Modificacao'] = m
        self.entradas[n_pagina]['Quadro'] = n_quadro
        self.entradas[n_pagina]['Tempo'] = 0
        self.entradas[n_pagina]['Referencia'] = 1

    # mostra o estado atual da TP
    def mostrar(self):
        for item in self.entradas:
            print(item)


class TLB:

    # inicializa a TLB
    def __init__(self, n_entradas):
        self.n_entradas = n_entradas
        self.entradas = self.init_entradas()
        self.ponteiro_relogio = 0

    # inicializa o dicionario entradas que representa as entradas da TLB
    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Validade': 0,
                'Pagina': -1,
                'Presenca': 0,
                'Modificacao': 0,
                'Quadro': -1,
                'Tempo': 0,
                'Referencia': 0,
                'Processo': -1
            }
            entradas.append(entrada)
        return entradas

    def limpar_processo(self, id_processo):
        for entrada in self.entradas:
            if entrada['Processo'] == id_processo:
                entrada['Validade'] = 0
                entrada['Pagina'] = -1
                entrada['Presenca'] = 0
                entrada['Modificacao'] = 0
                entrada['Quadro'] = -1
                entrada['Tempo'] = 0
                entrada['Referencia'] = 0
                entrada['Processo'] = -1

    def aumentar_tempo(self, n_pagina):

        for i in range(self.n_entradas):
            if self.entradas[i]['Pagina'] != n_pagina and self.entradas[i]['Quadro'] != -1:
                self.entradas[i]['Tempo'] += 1

                # Busca nas entradas da TLB uma pagina especifica e também ve se é válida a pagina
    def buscar(self, n_pagina, id_processo):
        for i, entrada in enumerate(self.entradas):

            if entrada['Validade'] == 1 and entrada['Pagina'] == n_pagina and entrada['Processo'] == id_processo:  # entrada encontrada
                self.entradas[i]['Tempo'] = 0
                self.entradas[i]['Referencia'] = 1
                self.aumentar_tempo(n_pagina)
                return self.entradas[i]['Quadro']

            if entrada['Validade'] == 0 and entrada['Quadro'] == -1:  # entrada vazia
                self.aumentar_tempo(n_pagina)
                return -2

        return -1   # entrada não encontrada

    def retirar_presenca(self, tempo):
        for entrada in self.entradas:
            if entrada['Tempo'] == tempo:
                entrada['Presenca'] = 0
                break

    # Atualiza uma entrada da TLB
    # Prec
    def atualizar(self, n_pagina, v, m, n_quadro, id_processo):
        for entrada in self.entradas:
            if entrada['Presenca'] == 0:
                entrada['Presenca'] = 1
                entrada['Validade'] = v
                entrada['Pagina'] = n_pagina
                entrada['Modificacao'] = m
                entrada['Quadro'] = n_quadro
                entrada['Tempo'] = 0
                entrada['Referencia'] = 1
                entrada['Processo'] = id_processo
                break

    def mostrar(self):
        for item in self.entradas:
            print(item)


class Processo:

    def __init__(self, estado, id_processo, n_entrada_tp):
        self.estado = estado
        self.id = id_processo
        self.tp = TP(n_entrada_tp)
        self.quantum_restante = 0
        self.operacoes_io = []

    def alterar_estado(self, novo_estado):
        self.estado = novo_estado


class EscalonadorProcessos:
    def __init__(self):
        self.fila_prontos = deque()
        self.processo_executando = None
        self.processos_bloqueados = []
        self.quantum = 3

    def adicionar_processo(self, processo):
        processo.quantum_restante = self.quantum
        self.fila_prontos.append(processo)

    def executar_processo(self):
        if self.processo_executando is None and self.fila_prontos:
            self.processo_executando = self.fila_prontos.popleft()
            self.processo_executando.alterar_estado("Executando")
            print(f"Processo {self.processo_executando.id} em execução")

    def preemptar_processo(self):
        if self.processo_executando:
            self.processo_executando.alterar_estado("Pronto")
            self.processo_executando.quantum_restante = self.quantum
            self.fila_prontos.append(self.processo_executando)
            self.processo_executando = None

    def bloquear_processo(self):
        if self.processo_executando:
            self.processo_executando.alterar_estado("Bloqueado")
            self.processos_bloqueados.append(self.processo_executando)
            self.processo_executando = None

    def desbloquear_processo(self, id_processo):
        for i, processo in enumerate(self.processos_bloqueados):
            if processo.id == id_processo:
                processo.alterar_estado("Pronto")
                self.fila_prontos.append(processo)
                del self.processos_bloqueados[i]
                break

    def terminar_processo(self):
        if self.processo_executando:
            self.processo_executando.alterar_estado("Terminado")
            self.processo_executando = None


class GerenciadorMemoria:

    # inicializa uma entrada do GerenciadorMemoria
    def __init__(self, tlb, mem_principal, mem_sec, tam_end_logico):
        self.mp = mem_principal
        self.ms = mem_sec
        self.tlb = tlb
        self.processos = []
        self.politica_sub = PoliticaSubstituicao()
        self.end_logico = self.init_end_logico(tam_end_logico)
        self.escalonador = EscalonadorProcessos()

    def init_end_logico(self, tam_end_logico):

        tam_pg = self.mp.tam_quadro  # tamanho da pg = tamando do quadro
        offset_bits = int(math.log(tam_pg, 2))  # pega o numero de bits para offset
        n_pagina_bits = int(tam_end_logico-offset_bits)

        end_logico = {
            '#Pagina': n_pagina_bits,
            'offset': offset_bits
        }

        return end_logico

    def criar_processo(self, n_entradas_tp, id_processo, tam_imagem):

        for processo in enumerate(self.processos):
            if processo.id == id_processo:
                print(f"Processo {id_processo} já existe")
                return

        n_paginas = tam_imagem//self.mp.tam_quadro

        # 1 bit de presenca e 1 de modificacao
        # Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
        # tam_entrada_tp = 2 + math.log(self.mp.n_quadros, 2)

        processo = Processo("Novo", id_processo, n_entradas_tp)
        self.processos.append(processo)
        self.escalonador.adicionar_processo(processo)

        if not self.ms.salvar(id_processo, n_paginas, [""]*self.mp.tam_quadro):
            print(f"Espaço insuficiente na Memória Secundária, não foi possível criar processo {id_processo}")
            self.processos.pop()
            return

        self.ms.mostrar()

    # Primeiro precisamos liberar as paginas presentes na MP, ou seja, os que estão na TP e depois na MS
    def terminar_processo(self, id_processo):
        self.ms.liberar_processo(id_processo)
        self.tlb.limpar_processo(id_processo)
        
        for i, processo in enumerate(self.processos):
            if processo.id == id_processo:
                tp = processo.tp
                for entrada in tp.entradas:
                    self.mp.liberar_quadro(entrada['Quadro'])
                del self.processos[i]
                break
        self.ms.mostrar()
        self.mp.mostrar()

    def mostrar_tp(self, id_processo):
        for i, processo in enumerate(self.processos):
            if processo.id == id_processo:
                self.processos[i].tp.mostrar()

    def traduzir_endereco(self, end_logico):
        end_fisico = bin(end_logico)[2:].zfill(16)   # remove prefixo '0b'e preenche com zeros a esquerda
        bits_pagina = self.end_logico['#Pagina']
        n_pagina = int(end_fisico[:bits_pagina], 2)
        offset = int(end_fisico[bits_pagina:self.end_logico['offset']], 2)
        return n_pagina, offset

    def transferir_mp(self, id_processo, n_pagina):

        quadro = self.ms.carregar(id_processo, n_pagina)

        if quadro is None:
            print(f"Página {n_pagina} do processo {id_processo} não encontrado na Memória Secundaria")
            return None

        n_quadro = self.mp.alocar_quadro(quadro['Processo'], quadro['Pagina'], quadro['Conteudo'])
        return n_quadro

    def add_entrada_tp(self, m, id_processo, n_pagina):
        novo_n_quadro = self.transferir_mp(id_processo, n_pagina)

        if novo_n_quadro is None:
            return None

        for i, processo in enumerate(self.processos):
            if processo.id == id_processo:
                self.processos[i].tp.atualizar(1, m, novo_n_quadro, n_pagina)
                self.processos[i].tp.mostrar()

        return novo_n_quadro

    def busca_pagina(self, id_processo, n_pagina, m):

        n_quadro_tlb = self.tlb.buscar(n_pagina, id_processo)  # Procura se a pagina esta na tlb

        if n_quadro_tlb != -1 and n_quadro_tlb != -2:  # Achou a pagina na TLB
            print("TLB hit!")
            self.tlb.mostrar()
            self.mostrar_tp(id_processo)
            return n_quadro_tlb

        else:  # Não achou a pagina na TLB
            tp = None
            for _,  processo in enumerate(self.processos):
                if processo.id == id_processo:
                    tp = processo.tp  # facilitar entendimento no uso da TP do processo
                    break

            if tp is None:
                print("Processo não existe")
                return None

            n_quadro_tp = tp.buscar(n_pagina, self.mp)  # Procura se a pagina esta na tp

            if n_quadro_tp == -2:  # TP ainda não está cheia
                print("TP ainda não está cheia! Adicionando entrada!")
                n_novo_quadro = self.add_entrada_tp(m, id_processo, n_pagina)

            elif n_quadro_tp == -1:  # TP não possui a Pagina
                n_novo_quadro = self.politica_sub.sub_tp(tp, self.mp, self.ms, id_processo, n_pagina, m)
                self.mostrar_tp(id_processo)

            else:  # TP possui a pagina
                n_novo_quadro = n_quadro_tp

            if n_novo_quadro is None:  # Indica que quadro não existe na mp
                return

            if n_quadro_tlb == -2:  # TLB não está cheia
                print("TLB ainda não está cheia! Adicionando entrada!")
                self.tlb.atualizar(n_pagina, 1, 0, n_novo_quadro, id_processo)
                self.tlb.mostrar()

            elif n_quadro_tlb == -1:  # TLB nao possui a Pagina
                self.politica_sub.sub_tlb(self.tlb, self.mp, n_novo_quadro, m, n_pagina, id_processo)
                self.tlb.mostrar()

            return n_novo_quadro

    def escrita_memoria(self, id_processo, end_logico, conteudo):

        n_pagina, offset = self.traduzir_endereco(end_logico)

        n_quadro = self.busca_pagina(id_processo, n_pagina, 1)
        self.mp.escrever(n_quadro, offset, conteudo)

    def leitura_memoria(self, id_processo, end_logico):

        n_pagina, offset = self.traduzir_endereco(end_logico)

        n_quadro = self.busca_pagina(id_processo, n_pagina, None)
        quadro = self.mp.ler(n_quadro)
        return quadro['Conteudo'][offset]

    def executar_instrucao_cpu(self, id_processo):
        if self.escalonador.processo_executando and self.escalonador.processo_executando.id == id_processo:
            self.escalonador.processo_executando.quantum_restante -= 1
            print(f"Executando instrução CPU para processo {id_processo}")
            
            if self.escalonador.processo_executando.quantum_restante <= 0:
                print(f"Quantum esgotado para processo {id_processo}")
                self.escalonador.preemptar_processo()
                self.escalonador.executar_processo()

    def executar_operacao_io(self, id_processo):
        if self.escalonador.processo_executando and self.escalonador.processo_executando.id == id_processo:
            print(f"Processo {id_processo} realizando operação I/O - bloqueando")
            self.escalonador.bloquear_processo()
            self.escalonador.executar_processo()

    def carregar_arquivo(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                linhas = arquivo.readlines()
                
            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                    
                partes = linha.split()
                operacao = partes[0]
                
                if operacao == 'C':
                    tamanho = int(partes[1])
                    id_processo = int(partes[2])
                    n_entrada_tp = int(math.pow(2, self.end_logico['#Pagina']))
                    self.criar_processo(n_entrada_tp, id_processo, tamanho)
                
                elif operacao == 'R':
                    id_processo = int(partes[1])
                    end_logico = int(partes[2])
                    resultado = self.leitura_memoria(id_processo, end_logico)
                    if resultado is not None:
                        print(f"Leitura: {resultado}")
                
                elif operacao == 'W':
                    id_processo = int(partes[1])
                    end_logico = int(partes[2])
                    conteudo = partes[3]
                    self.escrita_memoria(id_processo, end_logico, conteudo)
                
                elif operacao == 'P':
                    id_processo = int(partes[1])
                    self.executar_instrucao_cpu(id_processo)
                
                elif operacao == 'I':
                    id_processo = int(partes[1])
                    self.executar_operacao_io(id_processo)
                
                elif operacao == 'T':
                    id_processo = int(partes[1])
                    self.terminar_processo(id_processo)
                    
        except FileNotFoundError:
            print(f"Arquivo {caminho_arquivo} não encontrado")
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")


class PoliticaSubstituicao:

    @staticmethod
    def lru_tp(tp, mp, ms, id_processo, n_pagina, m):

        maior_tempo = -1
        idx_maior = -1

        for idx, entrada in enumerate(tp.entradas):
            if entrada['Presenca'] == 1 and entrada['Tempo'] > maior_tempo:
                maior_tempo = entrada['Tempo']
                idx_maior = idx

        entrada_subs = tp.entradas[idx_maior]  # pega entrada que será substituida por ter mais tempo sem ser executada

        tp.retirar_presenca(maior_tempo)

        quadro = mp.ler(entrada_subs['Quadro'])  # pegar quadro antigo da Mp
        mp.liberar_quadro(entrada_subs['Quadro'])  # libera o quadro da MP
        novo_quadro = ms.carregar(id_processo, n_pagina)  # carregar pagina desejada em um novo quadro
        ms.salvar(quadro['Processo'], 1, quadro['Conteudo'])  # salvar quadro antigo na MS

        if novo_quadro is None:  # verifica se página existe
            return None

        n_novo_quadro = mp.alocar_quadro(id_processo, n_pagina, novo_quadro['Conteudo'])
        tp.atualizar(1, m, n_novo_quadro, n_pagina)
        tp.atualizar(0, 0, -1, idx_maior)

        return n_novo_quadro

    @staticmethod
    def relogio_tp(tp, mp, ms, id_processo, n_pagina, m):
        while True:
            entrada = tp.entradas[tp.ponteiro_relogio]
            
            if entrada['Presenca'] == 1:
                if entrada['Referencia'] == 0:
                    quadro = mp.ler(entrada['Quadro'])
                    mp.liberar_quadro(entrada['Quadro'])
                    novo_quadro = ms.carregar(id_processo, n_pagina)
                    ms.salvar(quadro['Processo'], 1, quadro['Conteudo'])
                    
                    if novo_quadro is None:
                        return None
                    
                    n_novo_quadro = mp.alocar_quadro(id_processo, n_pagina, novo_quadro['Conteudo'])
                    old_idx = tp.ponteiro_relogio
                    tp.atualizar(1, m, n_novo_quadro, n_pagina)
                    tp.atualizar(0, 0, -1, old_idx)
                    
                    tp.ponteiro_relogio = (tp.ponteiro_relogio + 1) % tp.n_entradas
                    return n_novo_quadro
                else:
                    entrada['Referencia'] = 0
            
            tp.ponteiro_relogio = (tp.ponteiro_relogio + 1) % tp.n_entradas

    @staticmethod
    def lru_tlb(tlb, mp, n_quadro, m, n_pagina, id_processo):
        maior_tempo = 0
        for entrada in tlb.entradas:
            if entrada['Tempo'] > maior_tempo:
                maior_tempo = entrada['Tempo']

        tlb.retirar_presenca(maior_tempo)
        quadro = mp.ler(n_quadro)
        tlb.atualizar(n_pagina, 1, m, n_quadro, id_processo)

    @staticmethod
    def relogio_tlb(tlb, mp, n_quadro, m, n_pagina, id_processo):
        while True:
            entrada = tlb.entradas[tlb.ponteiro_relogio]
            
            if entrada['Presenca'] == 1:
                if entrada['Referencia'] == 0:
                    entrada['Presenca'] = 0
                    entrada['Validade'] = 1
                    entrada['Pagina'] = n_pagina
                    entrada['Modificacao'] = m
                    entrada['Quadro'] = n_quadro
                    entrada['Tempo'] = 0
                    entrada['Referencia'] = 1
                    entrada['Processo'] = id_processo
                    
                    tlb.ponteiro_relogio = (tlb.ponteiro_relogio + 1) % tlb.n_entradas
                    break
                else:
                    entrada['Referencia'] = 0
            else:
                entrada['Presenca'] = 1
                entrada['Validade'] = 1
                entrada['Pagina'] = n_pagina
                entrada['Modificacao'] = m
                entrada['Quadro'] = n_quadro
                entrada['Tempo'] = 0
                entrada['Referencia'] = 1
                entrada['Processo'] = id_processo
                break
            
            tlb.ponteiro_relogio = (tlb.ponteiro_relogio + 1) % tlb.n_entradas

    def sub_tp(self, tabela, mp, ms, id_processo, bits_pagina, m):

        print("Falta de Pagina!")

        while True:

            print("Escolha 1 para LRU e 2 para Relógio")
            try:
                op = int(input())
                if op == 1:
                    return self.lru_tp(tabela, mp, ms, id_processo, bits_pagina, m)
                elif op == 2:
                    return self.relogio_tp(tabela, mp, ms, id_processo, bits_pagina, m)
                else:
                    print("Digite as opções 1 ou 2!")
            except ValueError:
                print("Digite um número válido!")

    def sub_tlb(self, tabela, mp, n_quadro, m, n_pagina, id_processo):

        print("TLB miss")

        while True:

            print("Escolha 1 para LRU e 2 para Relógio")
            try:
                op = int(input())
                if op == 1:
                    return self.lru_tlb(tabela, mp, n_quadro, m, n_pagina, id_processo)
                elif op == 2:
                    return self.relogio_tlb(tabela, mp, n_quadro, m, n_pagina, id_processo)
                else:
                    print("Digite as opções 1 ou 2!")
            except ValueError:
                print("Digite um número válido!")


class InterfaceGrafica:
    def __init__(self, gm):
        self.gm = gm
        self.root = tk.Tk()
        self.root.title("Simulador de Gerenciamento de Memória")
        self.root.geometry("800x600")
        
        self.criar_widgets()
        
    def criar_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        frame_operacoes = ttk.Frame(notebook)
        notebook.add(frame_operacoes, text="Operações")
        
        frame_memoria = ttk.Frame(notebook)
        notebook.add(frame_memoria, text="Estado da Memória")
        
        self.criar_frame_operacoes(frame_operacoes)
        self.criar_frame_memoria(frame_memoria)
        
    def criar_frame_operacoes(self, parent):
        ttk.Button(parent, text="Carregar Arquivo", command=self.carregar_arquivo).pack(pady=5)
        
        ttk.Label(parent, text="Criar Processo:").pack(pady=5)
        frame_criar = ttk.Frame(parent)
        frame_criar.pack(pady=5)
        
        ttk.Label(frame_criar, text="ID:").grid(row=0, column=0)
        self.entry_id_criar = ttk.Entry(frame_criar, width=10)
        self.entry_id_criar.grid(row=0, column=1)
        
        ttk.Label(frame_criar, text="Tamanho:").grid(row=0, column=2)
        self.entry_tamanho = ttk.Entry(frame_criar, width=10)
        self.entry_tamanho.grid(row=0, column=3)
        
        ttk.Button(frame_criar, text="Criar", command=self.criar_processo).grid(row=0, column=4)
        
        ttk.Label(parent, text="Leitura de Memória:").pack(pady=5)
        frame_leitura = ttk.Frame(parent)
        frame_leitura.pack(pady=5)
        
        ttk.Label(frame_leitura, text="ID Processo:").grid(row=0, column=0)
        self.entry_id_leitura = ttk.Entry(frame_leitura, width=10)
        self.entry_id_leitura.grid(row=0, column=1)
        
        ttk.Label(frame_leitura, text="Endereço:").grid(row=0, column=2)
        self.entry_end_leitura = ttk.Entry(frame_leitura, width=10)
        self.entry_end_leitura.grid(row=0, column=3)
        
        ttk.Button(frame_leitura, text="Ler", command=self.ler_memoria).grid(row=0, column=4)
        
        ttk.Label(parent, text="Escrita de Memória:").pack(pady=5)
        frame_escrita = ttk.Frame(parent)
        frame_escrita.pack(pady=5)
        
        ttk.Label(frame_escrita, text="ID Processo:").grid(row=0, column=0)
        self.entry_id_escrita = ttk.Entry(frame_escrita, width=10)
        self.entry_id_escrita.grid(row=0, column=1)
        
        ttk.Label(frame_escrita, text="Endereço:").grid(row=0, column=2)
        self.entry_end_escrita = ttk.Entry(frame_escrita, width=10)
        self.entry_end_escrita.grid(row=0, column=3)
        
        ttk.Label(frame_escrita, text="Conteúdo:").grid(row=0, column=4)
        self.entry_conteudo = ttk.Entry(frame_escrita, width=10)
        self.entry_conteudo.grid(row=0, column=5)
        
        ttk.Button(frame_escrita, text="Escrever", command=self.escrever_memoria).grid(row=0, column=6)
        
        self.text_output = tk.Text(parent, height=15, width=80)
        self.text_output.pack(pady=10)
        
    def criar_frame_memoria(self, parent):
        self.text_memoria = tk.Text(parent, height=30, width=80)
        self.text_memoria.pack(pady=10)
        
        ttk.Button(parent, text="Atualizar Estado", command=self.atualizar_estado_memoria).pack(pady=5)
        
    def carregar_arquivo(self):
        arquivo = filedialog.askopenfilename(title="Selecionar arquivo de instruções")
        if arquivo:
            self.gm.carregar_arquivo(arquivo)
            self.log_output(f"Arquivo {arquivo} carregado com sucesso")
            
    def criar_processo(self):
        try:
            id_proc = int(self.entry_id_criar.get())
            tamanho = int(self.entry_tamanho.get())
            n_entrada_tp = int(math.pow(2, self.gm.end_logico['#Pagina']))
            self.gm.criar_processo(n_entrada_tp, id_proc, tamanho)
            self.log_output(f"Processo {id_proc} criado")
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos")
            
    def ler_memoria(self):
        try:
            id_proc = int(self.entry_id_leitura.get())
            endereco = int(self.entry_end_leitura.get())
            resultado = self.gm.leitura_memoria(id_proc, endereco)
            self.log_output(f"Leitura do processo {id_proc}, endereço {endereco}: {resultado}")
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos")
            
    def escrever_memoria(self):
        try:
            id_proc = int(self.entry_id_escrita.get())
            endereco = int(self.entry_end_escrita.get())
            conteudo = self.entry_conteudo.get()
            self.gm.escrita_memoria(id_proc, endereco, conteudo)
            self.log_output(f"Escrita no processo {id_proc}, endereço {endereco}: {conteudo}")
        except ValueError:
            messagebox.showerror("Erro", "Digite valores válidos")
            
    def log_output(self, mensagem):
        self.text_output.insert(tk.END, mensagem + "\n")
        self.text_output.see(tk.END)
        
    def atualizar_estado_memoria(self):
        self.text_memoria.delete(1.0, tk.END)
        
        estado = "=== ESTADO DA MEMÓRIA ===\n\n"
        
        estado += "MEMÓRIA PRINCIPAL:\n"
        for i, quadro in enumerate(self.gm.mp.quadros):
            if quadro['Processo'] == -1:
                estado += f"Quadro {i}: Livre\n"
            else:
                estado += f"Quadro {i}: Processo {quadro['Processo']}, Página {quadro['Pagina']}\n"
        
        estado += "\nTLB:\n"
        for i, entrada in enumerate(self.gm.tlb.entradas):
            if entrada['Validade'] == 1:
                estado += f"TLB {i}: Processo {entrada['Processo']}, Página {entrada['Pagina']}, Quadro {entrada['Quadro']}\n"
            else:
                estado += f"TLB {i}: Livre\n"
                
        estado += "\nPROCESSOS:\n"
        for processo in self.gm.processos:
            estado += f"Processo {processo.id}: Estado {processo.estado}\n"
            
        if self.gm.escalonador.processo_executando:
            estado += f"\nProcesso em execução: {self.gm.escalonador.processo_executando.id}\n"
        
        estado += f"Fila de prontos: {[p.id for p in self.gm.escalonador.fila_prontos]}\n"
        estado += f"Processos bloqueados: {[p.id for p in self.gm.escalonador.processos_bloqueados]}\n"
        
        self.text_memoria.insert(1.0, estado)
        
    def executar(self):
        self.root.mainloop()

def main():
    tam_quadro = int(input("Defina o tamanho do quadro/página:"))
    tam_end_logico = int(input("Digite o tamanho em bits do endereço lógico:"))
    n_entrada_tlb = int(input("Digite o numero de entradas da TLB:"))
    tam_mp = int(input("Digite o tamanho da memoria princpal:"))
    tam_mem_sec = int(input("Digite o tamanho da memoria secundaria:"))

    n_entrada_tp = int(math.pow(2, tam_end_logico))//tam_quadro
    n_quadro = tam_mp // tam_quadro

    tlb = TLB(n_entrada_tlb)
    mem_principal = MemoriaPrincipal(n_quadro, tam_quadro)
    mem_sec = MemoriaSecundaria(tam_mem_sec, tam_quadro)
    gm = GerenciadorMemoria(tlb, mem_principal, mem_sec, tam_end_logico)

    print("Escolha o modo de execução:")
    print("1 - Interface gráfica")
    print("2 - Interface de linha de comando")
    
    modo = input("Digite sua escolha: ")
    
    if modo == "1":
        interface = InterfaceGrafica(gm)
        interface.executar()
    else:
        while True:
            print("-------------------------------------------------")
            print("Bem vindo ao simulador de Gerenciador de Memoria! Digite a letra referente a opcao.")
            print("P - instrução a ser executada pela CPU")
            print("I - instrução de I/O")
            print("C - criação (submissão de processos)")
            print("R - pedido de leitura executado pela CPU em um endereço lógico")
            print("W - pedido de escrita executado pela CPU em um endereço lógico de um valor")
            print("T - terminação processo")
            print("A - carregar arquivo de instruções")
            print("S - sair")
            print("-------------------------------------------------")

            opcao = input().upper()

            if opcao == 'P':
                id_processo = int(input("Digite o id do processo:"))
                gm.executar_instrucao_cpu(id_processo)

            elif opcao == 'I':
                id_processo = int(input("Digite o id do processo:"))
                gm.executar_operacao_io(id_processo)

            elif opcao == 'C':
                tamanho = int(input("Digite o tamanho do processo:"))
                id_processo = int(input("Digite o id do processo:"))
                gm.criar_processo(n_entrada_tp, id_processo, tamanho)

            elif opcao == 'R':
                id_processo = int(input("Digite o id do processo:"))
                end_logico = int(input("Digite o endereço logico:"))
                leitura = gm.leitura_memoria(id_processo, end_logico)

                if leitura is not None:
                    print(f"Conteúdo lido: {leitura}")

            elif opcao == 'W':
                id_processo = int(input("Digite o id do processo:"))
                end_logico = int(input("Digite o endereço logico:"))
                conteudo = str(input("Digite o conteudo que deseja armazenar:"))
                gm.escrita_memoria(id_processo, end_logico, conteudo)

            elif opcao == 'T':
                id_processo = int(input("Digite o id do processo:"))
                gm.terminar_processo(id_processo)

            elif opcao == 'A':
                caminho = input("Digite o caminho do arquivo:")
                gm.carregar_arquivo(caminho)
                
            elif opcao == 'S':
                break

            else:
                print("Digite uma opção válida.")

if __name__ == "__main__":
    main()
