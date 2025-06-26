from enum import Enum
from page_table import PageTable

class ProcessState(Enum):
    NEW = 0,
    READY = 1,
    RUNNING = 2,
    BLOCKED = 4,
    EXIT = 5


class ProcessControlBlock:
    def __init__(self, pid, image_address, image_page_count):
        self.pid = pid
        self.state: ProcessState = ProcessState.NEW

        # a informação abaixo costuma ficar numa VMA (Virtual Memory Area), mas
        # colocamos aqui por simplicidade
        self.image_address: int = image_address
        self.process_page_count: int = image_page_count
        self.page_table: PageTable | None = None

        # ponteiros para listas
        self.prev: ProcessControlBlock | None = None
        self.next: ProcessControlBlock | None = None


    def end_process(self):
        self.state = ProcessState.EXIT
        self.image_address = -1

        self.image_address = -1
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
