from tabela_paginas import TP

class Processo:

    def __init__(self, estado, id_processo, n_entrada_tp):
        self.estado = estado
        self.id = id_processo
        self.tp = TP(n_entrada_tp)

    # def alterar_estado(self):
