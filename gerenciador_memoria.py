import math

from tabela_paginas import PageTable
from process_control_block import ProcessControlBlock
from politica_substituicao import PoliticaSubstituicao

# 1 bit de presenca e 1 de modificacao
# Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
# tam_entrada_tp = 2 + math.log(self.mp.n_quadros, 2)

class GerenciadorMemoria:
    def __init__(self, tlb, mem_principal, mem_sec, tam_end_logico):
        self.mp = mem_principal
        self.ms = mem_sec
        self.tlb = tlb

        self.politica_sub = PoliticaSubstituicao()
        self.end_logico = self.init_end_logico(tam_end_logico)


    def init_end_logico(self, tam_end_logico):
        tam_pg = self.mp.tam_quadro  # tamanho da pg = tamanho do quadro
        offset_bits = int(math.log(tam_pg, 2))  # pega o numero de bits para offset
        n_pagina_bits = int(tam_end_logico-offset_bits)

        end_logico = {
            '#Pagina': n_pagina_bits,
            'offset': offset_bits
        }
        return end_logico


    def criar_processo(self, processo_id, tam_imagem):
        if self.mp.ppt.processo_existe(processo_id):
            print(f"Processo {processo_id} já existe")
            return

        if not self.ms.tem_espaco_suficiente(tam_imagem):
            print(f"Espaço insuficiente na Memória Secundária, não foi possível criar processo {processo_id}")
            return

        n_paginas_processo = tam_imagem//self.mp.tam_quadro

        # salva a imagem do processo todo na MS
        end_inicial = self.ms.salvar(processo_id, n_paginas_processo, [""] * self.mp.tam_quadro)

        # adiciona processo na principal process table
        self.mp.ppt.adicionar_processo(processo_id)

        # aloca um control block e a page table
        pcb = ProcessControlBlock(processo_id, end_inicial, n_paginas_processo)
        pcb.page_table = PageTable(n_paginas_processo)

        self.mp.process_control_blocks.append(pcb)
        end_pcb = self.mp.process_control_blocks.size - 1

        # armazena o "endereço" do pcb na principal process table
        self.mp.ppt.update_referencia_pcb(processo_id, end_pcb)

        # traz as primeira pagina pra MP
        self.carregar_pagina_mp(processo_id, 0)


    def terminar_processo(self, id_processo):
        if not self.mp.ppt.processo_existe(id_processo):
            print(f"O Processo {id_processo} não existe")
            return

        end_control_block = self.mp.ppt.get_entrada_ppt(id_processo).pcb_end
        pcb = self.mp.process_control_blocks[end_control_block]

        # libera na memoria principal
        for e in pcb.page_table.entradas:
            if e['Presenca'] == 1:
                self.mp.liberar_quadro(e['Quadro'])

        # libera na memoria secundaria
        self.ms.liberar_espaco(pcb.end_inicial, pcb.process_page_count, id_processo)

        # limpa os dados do processo (exceto alguns metadados) e seta status para 'Exit'
        pcb.end_process()

        self.ms.mostrar()
        self.mp.mostrar()


    def mostrar_tp(self, id_processo):
        for i, pcb in enumerate(self.mp.process_control_blocks):
            if pcb.process_id == id_processo:
                self.mp.process_control_blocks[i].page_table.mostrar()


    def traduzir_endereco(self, end_logico):
        end_fisico = bin(end_logico)[2:].zfill(16)   # remove prefixo '0b'e preenche com zeros a esquerda
        bits_pagina = self.end_logico['#Pagina']
        n_pagina = int(end_fisico[:bits_pagina], 2)
        offset = int(end_fisico[bits_pagina:self.end_logico['offset']], 2)
        return n_pagina, offset


    def carregar_pagina_mp(self, id_processo, n_pagina):
        pcb_end = self.mp.ppt.get_entrada_ppt(id_processo).pcb_end
        control_block = self.mp.process_control_blocks[pcb_end]



        pagina = self.ms.carregar(id_processo, n_pagina)

        if pagina is None:
            print(f"Página {n_pagina} do processo {id_processo} não encontrado na Memória Secundaria")
            return None

        quadro = self.mp.alocar_quadro(pagina['Processo'], pagina['Pagina'], pagina['Conteudo'])
        return quadro


    def add_entrada_tp(self, m, id_processo, n_pagina):
        novo_n_quadro = self.carregar_pagina_mp(id_processo, n_pagina)

        if novo_n_quadro is None:
            return None

        for i, processo in enumerate(self.processos):
            if processo.id == id_processo:
                self.processos[i].tp.atualizar(1, m, novo_n_quadro, n_pagina)
                self.processos[i].tp.mostrar()

        return novo_n_quadro


    def busca_pagina(self, id_processo, n_pagina, m):
        n_quadro_tlb = self.tlb.buscar(n_pagina)  # Procura se a pagina esta na tlb

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
                self.tlb.atualizar(n_pagina, 1, 0, n_novo_quadro)
                self.tlb.mostrar()

            elif n_quadro_tlb == -1:  # TLB nao possui a Pagina
                self.politica_sub.sub_tlb(self.tlb, self.mp, n_novo_quadro, m)
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
