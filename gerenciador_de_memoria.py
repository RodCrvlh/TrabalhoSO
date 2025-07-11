import datetime as dt
from random import randint

import word as w

from MMU import MemoryManagementUnit
from translation_lookaside_buffer import TLB

from memoria_principal import MemoriaPrincipal
from memoria_secundaria import MemoriaSecundaria
from dispositivo_io import DispositivoIO

from frame_table_entry import FrameTableEntry, PageState
from process_control_block import ProcessControlBlock, ProcessState
from page_table import PageTable
from tipo_interrupt import TipoInterrupt

from instrucao_processo import InstrucaoProcesso


class GerenciadorMemoria:
    # politicas: 'lru', 'clock'
    def __init__(self, tlb: TLB, mem_principal: MemoriaPrincipal, mem_sec: MemoriaSecundaria, tam_end_logico: int, tam_quadro: int, politica_substituicao: str):
        self.mmu = MemoryManagementUnit(tlb, tam_end_logico, tam_quadro)

        self.mp: MemoriaPrincipal = mem_principal
        self.ms: MemoriaSecundaria = mem_sec

        # no linux, todos os processos são indexados em uma tabela hash chamada pidhash
        self.pid_hash: dict[str, ProcessControlBlock] = {}

        # listas dos processos
        self.ready_queue_head: ProcessControlBlock | None = None
        self.blocked_queue_head: ProcessControlBlock | None = None
        self.exited_processes: list[ProcessControlBlock] = []

        # estrutura indexada pelo frame number que descreve todos os frames (quadros) da memória principal.
        # é utilizado pelos algoritmos de substituição. no linux, é equivalente ao mem_map. o windows usa o PFN Database
        self.frame_table: dict[int, FrameTableEntry] = {}
        self.clock_pointer = 0

        # lista com os índices de quadros livres
        self.quadros_livres: list[int] = [i for i in range(self.mp.qtd_quadros)]

        self.dispositivos_IO: dict[str, DispositivoIO] = {}

        self.politica_sub = politica_substituicao


    def adicionar_instrucao_processo(self, id_processo: str, instrucao: InstrucaoProcesso):
        pcb = self.pid_hash.get(id_processo)
        if not pcb:
            print(f"O Processo {id_processo} não existe")
            return
        pcb.instrucoes_simuladas.append(instrucao)


    def criar_processo(self, id_processo: str, tam_imagem):
        if self.pid_hash.get(id_processo):
            print(f"Processo {id_processo} já existe")
            return

        qtd_paginas_processo = tam_imagem//self.mp.tam_quadro

        if self.mp_cheia() and not self.ms.tem_espaco_suficiente(qtd_paginas_processo):
            print(f"Espaço insuficiente na memória virtual, não foi possível criar o processo {id_processo}")
            return

        # cria o control block e adiciona ele na pid_hash
        pcb = ProcessControlBlock(id_processo, qtd_paginas_processo)
        self.pid_hash[id_processo] = pcb

        print(f"+ Processo {id_processo} criado com {qtd_paginas_processo} páginas")

        pcb.alloc_page_table(PageTable(qtd_paginas_processo)) # cria uma page table pro processo
        self.set_process_ready(pcb.pid) # admite o processo

        print(f"s - Processo {id_processo} setado como READY")

        print(f"Solicitando primeira página do processo {id_processo} pra MP.")
        self.solicita_pagina_da_ms(pcb, 0) # traz as primeira pagina pra MP (e pra page table)


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


    def set_process_running(self, pcb: ProcessControlBlock):
        if pcb.state == ProcessState.READY:
            self.ready_queue_head = self.pop_process(pcb, self.ready_queue_head)

        pcb.run()
        print(f"s - Processo {pcb.pid} setado como READY")



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

        if pcb.state == ProcessState.READY:
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

        # se não tem nem page table, não tem nada alocado, só retorna
        if not pcb.page_table:
            pcb.end_process()
            self.exited_processes.append(pcb)
            return

        quadros_pra_excluir_ms: list[int] = []
        for e in pcb.page_table.entradas:
            print("CRASHOU AQUI ", e.page_frame_number)
            fte = self.frame_table[e.page_frame_number]
            if e.presenca == 1:
                # libera na memoria principal
                self.liberar_quadro_mp(e.page_frame_number)
                if fte.swap_location != -1:
                    quadros_pra_excluir_ms.append(fte.swap_location)
            else:
                quadros_pra_excluir_ms.append(e.page_frame_number)
            fte.liberar()

        # libera na memoria secundaria
        self.libera_quadros_ms(quadros_pra_excluir_ms)

        # limpa os dados do processo (exceto alguns metadados), seta status para 'Exit' e
        # joga pra lista dos terminados
        pcb.end_process()
        self.exited_processes.append(pcb)


    def move_clock(self):
        ordem = sorted(self.frame_table.keys())

        clock_index = ordem.index(self.clock_pointer)

        if self.clock_pointer < len(ordem)-1:
            self.clock_pointer = ordem[clock_index + 1]
        elif self.clock_pointer == len(ordem)-1:
            self.clock_pointer = ordem[0]


    def solicita_pagina_da_ms(self, pcb: ProcessControlBlock, num_pagina: int):
        if not pcb.page_table:
            print(f"Processo {pcb.pid} não tem tabela de páginas alocadas. Abortando operação.")
            self.terminar_processo(pcb.pid)
            return

        if num_pagina > pcb.process_page_count or num_pagina < 0:
            print("Erro fatal. Número de página inválido. Abortando operação.")
            self.terminar_processo(pcb.pid)
            return

        pte = pcb.page_table.get_entrada(num_pagina)
        num_quadro_swap = pte.page_frame_number
        print(f"& Processo {pcb.pid} - Tabela de páginas acessada:")
        print("  ∟", pte.show_string())

        # como tá pedindo da MS, coloca o processo na fila de bloqueados
        print(f"s - Processo {pcb.pid} setado como BLOCKED")
        self.set_process_blocked(pcb.pid)

        if not pte.presenca and num_quadro_swap == -1:
            print(f"Buscando página do processo {pcb.pid} no arquivo original")
            self.ms.finge_que_ta_pegando_do_arquivo(num_pagina, pcb.pid, self.interrupt_handler) # não tá na região de swap, então seria pego do arquivo do programa
        else:
            print(f"Buscando página do processo {pcb.pid} na área de swap")
            self.ms.ler_bloco(num_quadro_swap, pcb.pid, num_pagina, self.interrupt_handler) # lê a pagina do swap

        # if pagina is None:
        #     print(f"Não foi possível carregar a pagina {num_pagina} do swap do processo {pcb.pid} para a MP")
        #     self.terminar_processo(pcb.pid)


    def interrupt_handler(self, tipo: TipoInterrupt, id_processo, num_pagina: int = -1, pagina: list[w.Word] | None = None):
        print(f"! ! ! interrupção recebida - {str(tipo)} para {id_processo}")
        pcb = self.pid_hash.get(id_processo)

        if not pcb:
            print(f"O Processo {id_processo} não existe")
            return

        if tipo == TipoInterrupt.OP_IO:
            print(f"Operação IO terminada. Processo {id_processo} setado novamente para Ready")
            self.set_process_ready(id_processo)

        elif tipo == TipoInterrupt.LEITURA_MS:
            if pagina:
                quadro = self.salva_pagina_na_mp(id_processo, num_pagina, pagina)

                print(f"Leitura da MS finalizada. Processo {id_processo} setado novamente para Ready")
                self.set_process_ready(id_processo)

                match pcb.reg_ultima_instrucao:
                    case "solicita_leitura_memoria_dado":
                        self.continua_leitura_memoria(pcb, quadro, w.TipoWord.DADO)
                    case "solicita_leitura_memoria_instrucao":
                        self.continua_leitura_memoria(pcb, quadro, w.TipoWord.INSTRUCAO)
                    case _:
                        return
                return
            else:
                print(f"A imagem do processo possivelmente está corrompida. Terminando processo {id_processo}.")
                self.terminar_processo(id_processo)

        elif tipo == TipoInterrupt.ESCRITA_MS:
            print(f"Escrita na MS finalizada. Processo {id_processo} setado novamente para Ready")
            quadro = self.salva_pagina_na_mp(id_processo, num_pagina, pagina)
            if pcb.reg_ultima_instrucao == "solicita_escrita_memoria":
                self.continua_escrita_memoria(pcb, quadro)


    def salva_pagina_na_mp(self, id_processo, num_pagina, pagina) -> int:
        print(f"> {id_processo} - Tentando salvar página {num_pagina} na MP")

        pcb = self.pid_hash.get(id_processo)

        if not pcb:
            print(f">>>>>>> O processo {id_processo} não existe. Abortando.")
            return -1

        if not pcb.page_table:
            print(f">>>>>>> Processo {pcb.pid} não tem tabela de páginas alocadas. Abortando operação.")
            self.terminar_processo(pcb.pid)
            return -1

        # tenta alocar um quadro na MP
        num_quadro = self.alocar_quadro_mp()

        if num_quadro == -1:
            print('memoria cheia, iniciando substituição')
            if self.politica_sub == 'LRU':
                num_quadro = self.substituir_LRU()
            else:
                num_quadro = self.substituir_clock()

        # escreve a página no quadro alocado
        self.mp.escrever_pagina(num_quadro, pagina)

        # antes de limpar o local de swap dessa pagina da tabela de paginas, guarda pra salvar na frame table
        pte = pcb.page_table.get_entrada(num_pagina)
        num_quadro_swap = pte.page_frame_number

        # registra o quadro na page table do processo
        pte = pcb.page_table.adicionar_quadro(num_pagina, num_quadro)

        # conecta essa pagina adicionada no quadro
        fte = self.frame_table[num_quadro]
        fte.setup(PageState.ACTIVE, pcb, pte)

        if num_quadro_swap != -1:
            fte.swap_location = num_quadro_swap

        fte.mark_used()

        self.move_clock()

        self.mmu.tlb.invalidar_entrada(num_pagina)
        self.mmu.tlb.atualizar(num_pagina, pte.presenca, pte.modificado, pte.page_frame_number)

        # com a pagina carregada, define o processo como pronto
        pcb.set_ready()

        return num_quadro


    def solicita_escrita_memoria(self, id_processo, end_logico_dec: int, conteudo: int):
        # pega o process control block
        pcb = self.pid_hash.get(id_processo)

        if not pcb or not pcb.page_table:
            print(f"O Processo {id_processo} não existe ou está corrompido. Operação de escrita abortada.")
            return

        end_logico_bin = self.mmu.create_end_logico_bin(end_logico_dec)
        num_quadro = self.mmu.buscar_pagina(end_logico_bin, pcb.page_table)

        pcb.reg_ultima_instrucao = "solicita_escrita_memoria"
        word = w.Word()
        word.set_dado(conteudo)
        pcb.reg_dado = word
        pcb.reg_endereco_logico = end_logico_bin

        # se achou o quadro na memória, só continua
        if num_quadro != -1:
            self.continua_escrita_memoria(pcb, num_quadro)
            return

        # se não achou, tenta carregar da swap
        self.solicita_pagina_da_ms(pcb, end_logico_bin.num_pag_int())


    def continua_escrita_memoria(self, pcb: ProcessControlBlock, num_quadro: int):
        if num_quadro == -1:
            print("Não foi possível completar a operação de escrita. Abortando.")
            return

        fte = self.frame_table[num_quadro]
        fte.mark_used()
        fte.check_modified()

        end_fisico = self.mmu.traduzir_endereco(pcb.reg_endereco_logico, num_quadro)

        self.mp.escrever(end_fisico, pcb.reg_dado)


    def solicita_leitura_memoria(self, id_processo, end_logico_dec: int) -> w.Word | None:
        # pega o process control block
        pcb = self.pid_hash.get(id_processo)

        if not pcb or not pcb.page_table:
            print(f"O Processo {id_processo} não existe ou está corrompido. Operação de escrita abortada.")
            return

        end_logico_bin = self.mmu.create_end_logico_bin(end_logico_dec)
        num_quadro = self.mmu.buscar_pagina(end_logico_bin, pcb.page_table)

        pcb.reg_endereco_logico = end_logico_bin

        if pcb.reg_ultima_instrucao == "executar_instrucao_cpu":
            pcb.reg_ultima_instrucao = "solicita_leitura_memoria_instrucao"
            tipo = w.TipoWord.INSTRUCAO
        else:
            pcb.reg_ultima_instrucao = "solicita_leitura_memoria_dado"
            tipo = w.TipoWord.DADO

        # se achou o quadro na memória, continua a leitura
        if num_quadro != -1:
            self.continua_leitura_memoria(pcb, num_quadro, tipo)

        # se não achou, tenta carregar da swap
        self.solicita_pagina_da_ms(pcb, end_logico_bin.num_pag_int())


    def continua_leitura_memoria(self, pcb: ProcessControlBlock, num_quadro: int, tipoLeitura: w.TipoWord):
        if num_quadro == -1:
            print("Não foi possível completar a operação de leitura. Abortando.")
            return None

        fte = self.frame_table[num_quadro]
        fte.mark_used()

        end_fisico = self.mmu.traduzir_endereco(pcb.reg_endereco_logico, num_quadro)
        word = self.mp.ler(end_fisico)

        # Se ele pega "lixo" da memória, converte pra uma instrução e segue daí. Se era
        # uma instrução armazenada, usa ela
        if tipoLeitura == w.TipoWord.INSTRUCAO and word.tipo != w.TipoWord.INSTRUCAO:
            word.define_random_instrucao()

        pcb.reg_dado = word

        # nesse simulador não temos PC, então se pediu pra ler uma instrução específica,
        # assumimos que será executada, então o código abaixo age como "program counter"
        self.continua_instrucao_cpu(pcb)


    def mp_cheia(self):
        return len(self.quadros_livres) == 0


    def porcentagem_mp_usada(self):
        return 1 - len(self.quadros_livres) / self.mp.qtd_quadros


    def porcentagem_swap_usada(self):
        return 1 - len(self.ms.blocos_livres) / self.ms.qtd_blocos


    def alocar_quadro_mp(self) -> int:
        if self.mp_cheia():
            print("MP está cheia! Não foi possível alocar um quadro.")
            return -1

        num_quadro = self.quadros_livres.pop(0)
        # como é só um simulador, para fins de desempenho ele só aloca uma página inascessada na hora que acessar
        if not num_quadro in self.frame_table:
            self.frame_table[num_quadro] = FrameTableEntry()

        self.frame_table[num_quadro].iniciar_alocacao()

        return num_quadro


    # como não houve grandes especificações para essa parte, os valores
    # utilizados são aleatórios.
    def executar_instrucao_cpu(self, id_processo, end_logico):
        pcb = self.pid_hash.get(id_processo)

        if not pcb or not pcb.page_table:
            print(f"O Processo {id_processo} não existe ou está corrompido. Execução de instrução de CPU abortado.")
            return

        pcb.reg_ultima_instrucao = "executar_instrucao_cpu"
        self.solicita_leitura_memoria(id_processo, end_logico)


    def continua_instrucao_cpu(self, pcb: ProcessControlBlock):
        word = pcb.reg_dado

        a = randint(-2147483648, 2147483647)
        b = randint(-2147483648, 2147483647)

        if word.instrucao == w.Instrucao.SOMA:
            print(f"Executando soma.\n{a} + {b} = {a + b}")
        else:
            print(f"Executando subtracao.\n{a} - {b} = {a - b}")


    def executar_operacao_io(self, id_processo, id_dispositivo_IO):
        pcb = self.pid_hash.get(id_processo)

        if not pcb or not pcb.page_table:
            print(f"O Processo {id_processo} não existe ou está corrompido. Execução de instrução de CPU abortado.")
            return

        if id_dispositivo_IO not in self.dispositivos_IO:
            self.dispositivos_IO[id_dispositivo_IO] = DispositivoIO(id_dispositivo_IO)

        self.dispositivos_IO[id_dispositivo_IO].instrucao_IO(id_processo, self.interrupt_handler)

        # como é IO, coloca como bloqueado
        self.set_process_blocked(id_processo)


    #
    # Desalocar nas memórias
    #

    def liberar_quadro_mp(self, num_quadro):
        if num_quadro >= self.mp.qtd_quadros:
            print("Quadro inexistente")
            return

        fte = self.frame_table[num_quadro]
        fte.liberar()

        self.quadros_livres.append(num_quadro)


    def libera_quadros_ms(self, quadros: list[int]):
        for num_quadro in quadros:
            self.ms.liberar_bloco(num_quadro)


    #
    # Politicas de substituicao
    #

    def substituir_LRU(self) -> int:
        oldest_timestamp = dt.datetime.now().timestamp()
        oldest_frame_number = 0

        # seleciona a página, dentre todos os frames, q não é acessada há mais tempo
        for frame_number, fte in self.frame_table.items():
            if fte.timestamp < oldest_timestamp:
                oldest_timestamp = fte.timestamp
                oldest_frame_number = frame_number

        fte_vitima = self.frame_table[oldest_frame_number]

        if not fte_vitima.owner_process or not fte_vitima.page_table_entry:
            return -1

        # se a página foi modificada, salva o estado atual dela no disco
        if fte_vitima.modified == 1:
            pagina = self.mp.ler_quadro(oldest_frame_number)
            local_swap = self.frame_table[oldest_frame_number].swap_location
            self.ms.escrever_pagina(local_swap, pagina)
            # atualiza a page table
            pte = fte_vitima.page_table_entry
            pte.tira_presenca()
            pte.page_frame_number = local_swap

        # libera o quadro da tabela de paginas e da frame table
        fte_vitima.page_table_entry.tira_presenca()
        fte_vitima.liberar()

        return oldest_frame_number


    def substituir_clock(self) -> int:
        # enquanto achar 1 no bit used, vai movendo o clock e trocando todo 1 pra 0
        while self.frame_table[self.clock_pointer].used != 0:
            self.frame_table[self.clock_pointer].unmark_used()
            self.move_clock()

        # quando achar um used = 0, essa faz o processo pra salvar a página na MS e
        # liberar a vítima
        fte_vitima = self.frame_table[self.clock_pointer]

        if not fte_vitima.owner_process or not fte_vitima.page_table_entry:
            return -1

        # se a página foi modificada, salva o estado atual dela no disco
        if fte_vitima.modified == 1:
            pagina = self.mp.ler_quadro(self.clock_pointer)
            local_swap = self.frame_table[self.clock_pointer].swap_location
            self.ms.escrever_pagina(local_swap, pagina)
            # atualiza a page table
            pte = fte_vitima.page_table_entry
            pte.tira_presenca()
            pte.page_frame_number = local_swap

        fte_vitima.page_table_entry.tira_presenca()
        fte_vitima.liberar()

        return self.clock_pointer
