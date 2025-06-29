# pelo escopo do trabalho, alguns bits não foram implementadas:
# - bits de acesso (permissões de escrita, leitura, execução)

class PageTableEntry:
    def __init__(self, presenca = 0, modificado = 0, num_quadro = -1):
        self.page_frame_number: int = num_quadro
        self.presenca = presenca
        self.modificado = modificado

    def set(self, num_quadro, presenca = 1, modificado = 0):
        self.presenca = presenca
        self.modificado = modificado
        self.page_frame_number = num_quadro

    def tira_presenca(self):
        self.presenca = 0

    def show_string(self):
        return f'Quadro: {self.page_frame_number} | P: {self.presenca} | M: {self.modificado}'


class PageTable:
    def __init__(self, qtd_entradas):
        self.qtd_entradas = qtd_entradas
        self.entradas: list[PageTableEntry] = []

        for _ in range(self.qtd_entradas):
            entrada = PageTableEntry()
            self.entradas.append(entrada)


    def remover_presenca(self, num_pagina):
        entrada = self.entradas[num_pagina]
        entrada.presenca = 0


    def adicionar_quadro(self, num_pagina, num_quadro):
        entrada = self.entradas[num_pagina]
        entrada.set(num_quadro)
        return entrada


    def get_entrada(self, n_pagina):
        return self.entradas[n_pagina]


    def buscar_quadro(self, n_pagina):
        if self.entradas[n_pagina].presenca == 1:  # Achou a pagina na TP
            return self.entradas[n_pagina].quadro
        return -1 # Não achou pagina na TP


    def esvaziar(self):
        self.qtd_entradas = 0
        self.entradas = []


    # mostra o estado atual da TP
    def mostrar(self):
        for i, entrada in enumerate(self.entradas):
            print(i, entrada.show_string())
