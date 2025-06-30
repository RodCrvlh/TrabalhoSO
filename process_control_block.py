from enum import Enum
from page_table import PageTable
import word as w
from MMU import EnderecoLogico

from instrucao_processo import InstrucaoProcesso

class ProcessState(Enum):
    NEW = 0,
    READY = 1,
    RUNNING = 2,
    BLOCKED = 4,
    EXIT = 5


class ProcessControlBlock:
    def __init__(self, pid, image_page_count):
        self.pid = pid
        self.state: ProcessState = ProcessState.NEW

        self.process_page_count: int = image_page_count
        self.page_table: PageTable | None = None

        # ponteiros para listas
        self.prev: ProcessControlBlock | None = None
        self.next: ProcessControlBlock | None = None

        # valor dos registradores salvos
        self.reg_endereco_logico: EnderecoLogico = EnderecoLogico(bin(0), bin(0))
        self.reg_dado: w.Word = w.Word().fill_with_trash()
        self.reg_ultima_instrucao: str = ""

        # instrucoes
        self.pc = 0
        self.instrucoes_simuladas: list[InstrucaoProcesso] = []


    def end_process(self):
        self.state = ProcessState.EXIT
        self.process_page_count = 0

        if self.page_table:
            self.page_table.esvaziar()


    def alloc_page_table(self, page_table: PageTable):
        self.page_table = page_table


    def set_ready(self):
        self.state = ProcessState.READY


    def block(self):
        self.state = ProcessState.BLOCKED


    def run(self):
        self.state = ProcessState.RUNNING
