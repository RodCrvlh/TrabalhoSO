import datetime as dt

from MMU import MemoryManagementUnit
from memoria_principal import MemoriaPrincipal
from memoria_secundaria import MemoriaSecundaria

from page_table import PageTable
from frame_table_entry import FrameTableEntry, PageState
from process_control_block import ProcessControlBlock, ProcessState

from translation_lookaside_buffer import TLB

# 1 bit de presenca e 1 de modificacao
# Usamos log na base 2 porque com 1024 quadros por exemplo, poderemos ter 10 bits para endereçar os quadros
# tam_entrada_tp = 2 + math.log(self.mp.n_quadros, 2)


class GerenciadorMemoria:
    # politicas: 'lru', 'clock'
    def __init__(self, tlb: TLB, mem_principal: MemoriaPrincipal, mem_sec: MemoriaSecundaria, tam_end_logico: int, tam_quadro: int, politica_substituicao: str):
        self.mmu = MemoryManagementUnit(tam_end_logico, tam_quadro)

        self.mp: MemoriaPrincipal = mem_principal
        self.ms: MemoriaSecundaria = mem_sec
        self.tlb: TLB = tlb

        # no linux, todos os processos são indexados em uma tabela hash chamada pidhash
        self.pid_hash: dict[str, ProcessControlBlock] = {}

        self.ready_queue_head: ProcessControlBlock | None = None
        self.blocked_queue_head: ProcessControlBlock | None = None

        # estrutura indexada pelo frame number que descreve todos os frames (quadros) da memória principal.
        # é utilizado pelos algoritmos de substituição. no linux, é equivalente ao mem_map. o windows usa o PFN Database
        self.frame_table: list[FrameTableEntry] = []
        self.clock_pointer = 0

        # lista com os índices de quadros livres
        self.quadros_livres: list[int] = []

        # preenche a frame table com estados iniciais
        for i in range(self.mp.qtd_quadros):
            self.frame_table.append(FrameTableEntry())
            self.quadros_livres.append(i)

        self.politica_sub = politica_substituicao

    def criar_processo(self, id_processo: str, tam_imagem):
        if self.pid_hash.get(id_processo):
            print(f"Processo {id_processo} já existe")
            return

        qtd_paginas_processo = tam_imagem//self.mp.tam_quadro

        if not self.ms.tem_espaco_suficiente(qtd_paginas_processo):
            print(f"Espaço insuficiente na Memória Secundária, não foi possível criar processo {id_processo}")
            return

        # cria a imagem do processo todo na MS
        end_inicial = self.ms.alocar_espaco(qtd_paginas_processo)

        # cria o control block e adiciona ele na pid_hash
        pcb = ProcessControlBlock(id_processo, end_inicial, qtd_paginas_processo)
        self.pid_hash.update(id_processo = pcb)

        pcb.alloc_page_table(PageTable(qtd_paginas_processo))

        # admite o processo
        self.set_process_ready(pcb.pid)

        # traz as primeira pagina pra MP
        self.carregar_pagina_pra_mp(id_processo, 0)

    # tira o processo da lista passada e retorna a cabeça da lista
    def pop_process(self, process: ProcessControlBlock, queue_head: ProcessControlBlock | None):
        if process.prev == None:
            queue_head = process.next
            process.next = None
            return queue_head

        process.prev.next = process.next
        process.prev = None
        process.next = None
        return queue_head

    # coloca o processo no final da lista passada e returna a cabeça da lista
    def append_process(self, process: ProcessControlBlock, queue_head: ProcessControlBlock | None):
        if not queue_head:
            return process

        last = queue_head
        while last.next != None:
            last = last.next

        last.next = process
        process.prev = last
        return queue_head

    # define o processo como pronto, colocando-o na fila de pronto
    def set_process_ready(self, process_id):
        pcb = self.pid_hash.get(process_id)

        if not pcb:
            print(f"O Processo {process_id} não existe")
            return

        if pcb.state == ProcessState.READY:
            print(f"O Processo {process_id} já estava pronto")
            return

        if pcb.state == ProcessState.BLOCKED:
            self.blocked_queue_head = self.pop_process(pcb, self.blocked_queue_head)

        pcb.set_ready()
        self.ready_queue_head = self.append_process(pcb, self.ready_queue_head)

    # define o processo como bloqueado, colocando-o na fila de bloqueado
    def set_process_blocked(self, process_id):
        pcb = self.pid_hash.get(process_id)

        if not pcb:
            print(f"O Processo {process_id} não existe")
            return

        if pcb.state == ProcessState.BLOCKED:
            self.blocked_queue_head = self.pop_process(pcb, self.blocked_queue_head)

        if pcb.state == ProcessState.BLOCKED:
            self.ready_queue_head = self.pop_process(pcb, self.ready_queue_head)

        pcb.block()
        self.blocked_queue_head = self.append_process(pcb, self.blocked_queue_head)

    def terminar_processo(self, id_processo):
        pcb = self.pid_hash.get(id_processo)

        if not pcb:
            print(f"O Processo {id_processo} não existe")
            return

        # tira da fila, se ele estiver em alguma
        if pcb.state == ProcessState.BLOCKED:
            self.blocked_queue_head = self.pop_process(pcb, self.blocked_queue_head)

        if pcb.state == ProcessState.READY:
            self.ready_queue_head = self.pop_process(pcb, self.ready_queue_head)

        # se não tem nem page table, não tem nada alocado, só ignora
        if not pcb.page_table:
            return

        # libera na memoria principal
        for e in pcb.page_table.entradas:
            if e.presenca == 1:
                self.liberar_quadro_mp(e.quadro)

        # libera na memoria secundaria
        self.ms.liberar_espaco(pcb.image_address, pcb.process_page_count)

        # limpa os dados do processo (exceto alguns metadados) e seta status para 'Exit'
        pcb.end_process()

    def move_clock(self):
        if self.clock_pointer < len(self.frame_table):
            self.clock += 1

        if self.clock_pointer == len(self.frame_table):
            self.clock = 0

    def carregar_pagina_pra_mp(self, id_processo, num_pagina):
        # pega o process control block
        pcb = self.pid_hash.get(id_processo)

        if not pcb:
            print(f"O Processo {id_processo} não existe")
            return -1

        # calcula o endereço da pagina na memoria secundária
        # PLACEHOLDER: TEM Q ARRUMAR ESSA FORMULA
        endereco_ms = pcb.image_address + num_pagina

        # lê a página da MS
        pagina = self.ms.ler_bloco(endereco_ms)

        if pagina is None:
            print(f"Página {num_pagina} do processo {id_processo} não encontrado na Memória Secundaria")
            return -1

        # tenta alocar o quadro na MP
        endereco_quadro = self.alocar_quadro_mp()

        if endereco_quadro == -1:
            print('memoria cheia, iniciando substituição')
            if self.politica_sub == 'LRU':
                endereco_quadro = self.substituir_LRU()
            else:
                endereco_quadro = self.substituir_clock()

        # escreve a página no quadro alocado
        self.mp.escrever_pagina(endereco_quadro, pagina)

        # se o processo não tem page table por algum motivo, aborta e libera o quadro alocado
        if not pcb.page_table:
            print(f"Processo {id_processo} não tem tabela de páginas alocadas. Liberando o quadro alocado e abortando operação.")
            self.liberar_quadro_mp(endereco_quadro)
            return -1

        # registra o quadro na page table do processo
        pcb.page_table.adicionar_pagina(num_pagina, endereco_quadro)

        # conecta essa pagina adicionada
        self.frame_table[endereco_quadro].setup(PageState.ACTIVE, pcb, endereco_ms)
        self.frame_table[endereco_quadro].mark_used()
        self.move_clock()

        # com a pagina carregada, define o processo como pronto
        pcb.set_ready()

        return endereco_quadro

    def busca_pagina(self, id_processo, num_pagina):
        # pega o process control block
        pcb = self.pid_hash.get(id_processo)

        if not pcb:
            print(f"O Processo {id_processo} não existe")
            return -1

        # procura se a pagina esta na tlb
        num_quadro_tlb = self.tlb.buscar(num_pagina)

        if num_quadro_tlb != -1:
            print("TLB hit!")
            return num_quadro_tlb

        if not pcb.page_table:
            print(f"Processo {id_processo} não tinha page table. Busca de página abortada.")
            return -1

        # busca o quadro na tabela de paginas
        num_quadro_tp = pcb.page_table.buscar_quadro(num_pagina)

        if num_quadro_tp != -1:
            print("TP hit!")
            num_quadro = num_quadro_tp
        else:
            # se não achou, carrega da MS -> MP -> TP
            num_quadro = self.carregar_pagina_pra_mp(id_processo, num_pagina)

        if num_quadro == -1:
            print("quadro não encontrado")
            return -1

        print("Atualizando TLB")
        self.tlb.atualizar(num_pagina, 1, 0, num_quadro)
        self.tlb.mostrar()

        return num_quadro

    def escrita_memoria(self, id_processo, end_logico, conteudo):
        num_pagina, offset = self.mmu.traduzir_endereco(end_logico)

        num_quadro = self.busca_pagina(id_processo, num_pagina)

        fte = self.frame_table[num_quadro]
        fte.mark_used()
        fte.check_modified()

        self.mp.escrever(num_quadro, offset, conteudo)

    def leitura_memoria(self, id_processo, end_logico):
        num_pagina, offset = self.mmu.traduzir_endereco(end_logico)

        num_quadro = self.busca_pagina(id_processo, num_pagina)

        fte = self.frame_table[num_quadro]
        fte.mark_used()

        quadro = self.mp.ler(num_quadro, offset)
        return quadro[offset]

    def mp_cheia(self):
        return len(self.quadros_livres) == 0

    def alocar_quadro_mp(self) -> int:
        if self.mp_cheia():
            print("MP está cheia! Não foi possível alocar um quadro.")
            return -1

        endereco_quadro = self.quadros_livres.pop()
        self.frame_table[endereco_quadro].iniciar_alocacao()

        return endereco_quadro

    def liberar_quadro_mp(self, end_quadro):
        if end_quadro >= self.mp.qtd_quadros:
            print("Quadro inexistente")
            return

        fte = self.frame_table[end_quadro]
        fte.liberar()

        self.quadros_livres.append(end_quadro)

    #
    # Politicas de substituicao
    #

    def substituir_LRU(self) -> int:
        oldest_timestamp = dt.datetime.now().timestamp()
        oldest_frame_number = 0

        # seleciona a página, dentre todos os frames, q não é acessada há mais tempo
        for frame_number, fte in enumerate(self.frame_table):
            if fte.timestamp < oldest_timestamp:
                oldest_timestamp = fte.timestamp
                oldest_frame_number = frame_number

        fte_vitima = self.frame_table[oldest_frame_number]

        if not fte_vitima.owner_process or not fte_vitima.pte:
            return -1

        # se a página foi modificada, salva o estado atual dela no disco
        if fte_vitima.modified == 1:
            pagina = self.mp.ler_quadro(oldest_frame_number)
            endereco = fte_vitima.owner_process.image_address + fte_vitima.virtual_page_number
            self.ms.escrever_pagina(endereco, pagina)

        # libera o quadro da tabela de paginas e da frame table
        fte_vitima.pte.tira_presenca()
        fte_vitima.liberar()

        return oldest_frame_number

    def executar_instrucao_cpu(self, id_processo, end_logico):
        print("Função não implementada ainda")

    def executar_operacao_io(self, id_processo, end_logico):
        print("Função não implementada ainda")

    def substituir_clock(self) -> int:
        # enquanto achar 1 no bit used, vai movendo o clock e trocando todo 1 pra 0
        while self.frame_table[self.clock_pointer].used != 0:
            self.frame_table[self.clock_pointer].unmark_used()
            self.move_clock()

        # quando achar um used = 0, essa faz o processo pra salvar a página na MS e
        # liberar a vítima
        fte_vitima = self.frame_table[self.clock_pointer]

        if not fte_vitima.owner_process or not fte_vitima.pte:
            return -1

        # se a página foi modificada, salva o estado atual dela no disco
        if fte_vitima.modified == 1:
            pagina = self.mp.ler_quadro(self.clock_pointer)
            endereco = fte_vitima.owner_process.image_address + fte_vitima.virtual_page_number
            self.ms.escrever_pagina(endereco, pagina)

        fte_vitima.pte.tira_presenca()
        fte_vitima.liberar()

        return self.clock_pointer
