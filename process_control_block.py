from tabela_paginas import PageTable

class ProcessControlBlock:
    page_table: PageTable

    def __init__(self, process_id, end_inicial, process_page_count):
        self.process_id = process_id
        self.status = None
        self.initial_execution_point_adress = end_inicial
        self.process_page_count = process_page_count


    def end_process(self):
        self.status = 'Exit'
        self.initial_execution_point_adress = -1
        self.page_table.esvaziar()
