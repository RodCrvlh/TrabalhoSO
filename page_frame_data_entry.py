import datetime as dt
from enum import Enum

from page_table import PageTableEntry
from process_control_block import ProcessControlBlock

class PageState(Enum):
    FREE = 0 # tá livre, ninguém acessando
    ACTIVE = 1 # alguém referencia
    TRANSITION_IN_PROGRESS = 2 # I/O ou sendo movido entre listas
    LOCKED = 3 # preso na memória, normalmente páginas do kernel

# alguns campos não foram implementados aqui por conta do escopo trabalho:
# - reference count, por não ter endereçamento compartilhado
# - protection bits, já que os comandos são apenas simulados
class FrameTableEntry:
    def __init__(self):
        self.page_state: PageState = PageState.FREE
        self.modified = 0

        self.owner_process: ProcessControlBlock | None = None
        self.pte: PageTableEntry | None = None
        self.virtual_page_number: int = 0

        self.timestamp = 0
        self.used = 0


    def setup(self, page_state: PageState, owner_process: ProcessControlBlock, virtual_page_number):
        self.page_state = page_state

        self.owner_process = owner_process
        self.virtual_page_number = virtual_page_number
        self.modified = 0
        self.timestamp = dt.datetime.now().timestamp()


    def iniciar_alocacao(self):
        self.page_state = PageState.TRANSITION_IN_PROGRESS

    def liberar(self):
        self.page_state = PageState.FREE

    def reset_time(self):
        self.timestamp = dt.datetime.now().timestamp()

    def check_modified(self):
        self.modified = 1

    def mark_used(self):
        self.used = 1

    def unmark_used(self):
        self.used = 0
