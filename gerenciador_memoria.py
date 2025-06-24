from tabela_paginas import PageTable
from process_control_block import ProcessControlBlock
from politica_substituicao import PoliticaSubstituicao
from principal_process_table import PrincipalProcessTable

from MMU import MMU

# 1 bit de presenca e 1 de modificacao
# Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
# tam_entrada_tp = 2 + math.log(self.mp.n_quadros, 2)

class GerenciadorMemoria:
    def __init__(self, tlb, mem_principal, mem_sec, tam_end_logico, tam_quadro):
        self.mmu = MMU(tam_end_logico, tam_quadro)

        self.mp = mem_principal
        self.ms = mem_sec
        self.tlb = tlb

        self.ppt = PrincipalProcessTable()
        self.process_control_blocks = []

        self.politica_sub = PoliticaSubstituicao()


    def criar_processo(self, processo_id, tam_imagem):
        if self.ppt.processo_existe(processo_id):
            print(f"Processo {processo_id} já existe")
            return

        if not self.ms.tem_espaco_suficiente(tam_imagem):
            print(f"Espaço insuficiente na Memória Secundária, não foi possível criar processo {processo_id}")
            return

        n_paginas_processo = tam_imagem//self.mp.tam_quadro

        # salva a imagem do processo todo na MS
        end_inicial = self.ms.salvar(processo_id, n_paginas_processo, [""] * self.mp.tam_quadro)

        # adiciona processo na principal process table
        self.ppt.adicionar_processo(processo_id)

        # aloca um control block e a page table
        pcb = ProcessControlBlock(processo_id, end_inicial, n_paginas_processo)
        pcb.page_table = PageTable(n_paginas_processo)

        self.process_control_blocks.append(pcb)
        end_pcb = len(self.process_control_blocks) - 1

        # armazena o "endereço" do pcb na principal process table
        self.ppt.update_referencia_pcb(processo_id, end_pcb)

        # traz as primeira pagina pra MP
        self.carregar_pagina_mp(processo_id, 0)


    def terminar_processo(self, id_processo):
        if not self.ppt.processo_existe(id_processo):
            print(f"O Processo {id_processo} não existe")
            return

        end_control_block = self.ppt.get_entrada_ppt(id_processo).pcb_end
        pcb = self.process_control_blocks[end_control_block]

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
        if not self.ppt.processo_existe(id_processo):
            print(f"O Processo {id_processo} não existe")
            return

        for pcb in self.process_control_blocks:
            if pcb.process_id == id_processo:
                pcb.page_table.mostrar()


    def carregar_pagina_mp(self, id_processo, n_pagina):
        if not self.ppt.processo_existe(id_processo):
            print(f"O Processo {id_processo} não existe")
            return -1

        # pega o process control block
        pcb_end = self.ppt.get_entrada_ppt(id_processo).pcb_end
        control_block = self.process_control_blocks[pcb_end]

        # calcula o endereço da pagina na memoria secundária
        endereco_ms = control_block.initial_execution_point_adress + n_pagina

        # lê a página da MS
        pagina = self.ms.ler_bloco(endereco_ms)

        if pagina is None:
            print(f"Página {n_pagina} do processo {id_processo} não encontrado na Memória Secundaria")
            return -1

        # aloca o quadro na MP e escreve a página nele
        numero_quadro = self.mp.alocar_quadro()
        self.mp.escrever_pagina(numero_quadro, pagina)

        # registra o quadro na page table do processo
        control_block.page_table.adicionar_pagina(n_pagina, numero_quadro)

        return numero_quadro


    def busca_pagina(self, id_processo, n_pagina, m):
        if not self.ppt.processo_existe(id_processo):
            print(f"O Processo {id_processo} não existe")
            return

        # procura se a pagina esta na tlb
        num_quadro_tlb = self.tlb.buscar(n_pagina)

        if num_quadro_tlb != -1:
            print("TLB hit!")
            return num_quadro_tlb

        pcb_end = self.ppt.get_entrada_ppt(id_processo).pcb_end
        control_block = self.process_control_blocks[pcb_end]

        # busca o quadro na tabela de paginas
        num_quadro_tp = control_block.page_table.buscar_quadro(n_pagina)

        if num_quadro_tp != -1:
            print("TP hit!")
            num_quadro = num_quadro_tp
        else:
            # se não achou, carrega da MS -> MP -> TP
            num_quadro = self.carregar_pagina_mp(id_processo, n_pagina)

        if num_quadro == -1:
            print("quadro não encontrado")
            return -1

        if self.tlb.ta_cheio():
            print("TLB cheia, substituindo.")
            self.politica_sub.sub_tlb(self.tlb, self.mp, num_quadro, m)
            self.tlb.mostrar()
        else:
            print("TLB ainda não está cheia! Adicionando entrada.")
            self.tlb.atualizar(n_pagina, 1, 0, num_quadro)
            self.tlb.mostrar()

        return num_quadro


    def escrita_memoria(self, id_processo, end_logico, conteudo):
        n_pagina, offset = self.mmu.traduzir_endereco(end_logico)

        n_quadro = self.busca_pagina(id_processo, n_pagina, 1)
        self.mp.escrever(n_quadro, offset, conteudo)


    def leitura_memoria(self, id_processo, end_logico):
        n_pagina, offset = self.mmu.traduzir_endereco(end_logico)

        n_quadro = self.busca_pagina(id_processo, n_pagina, None)
        quadro = self.mp.ler(n_quadro)
        return quadro['Conteudo'][offset]
