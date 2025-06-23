class PageTable:
    def __init__(self, n_entradas):
        self.n_entradas = n_entradas
        self.entradas = self.init_entradas()

    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Presenca':  0,
                'Modificacao': 0,
                'Quadro': -1,
                'Tempo': 0 # O tempo serve para politica LRU, significa quantas buscas foram feitas sem ele ser acessado
            }
            entradas.append(entrada)
        return entradas

    def aumentar_tempo_outras(self, n_pagina):
        print(f"pg:{n_pagina}")
        print(f"n_entradas:{self.n_entradas}")

        for i in range(self.n_entradas):
            if i != n_pagina and self.entradas[i]['Quadro'] != -1:
                print(self.entradas[i]['Tempo'])
                self.entradas[i]['Tempo'] += 1

    def buscar_quadro(self, n_pagina):
        self.aumentar_tempo_outras(n_pagina)

        if self.entradas[n_pagina]['Presenca'] == 1:  # Achou a pagina na TP
            self.entradas[n_pagina]['Tempo'] = 0
            return self.entradas[n_pagina]['Quadro']

        return -1 # Não a pagina na TP

    def retirar_presenca(self, tempo):
        for entrada in self.entradas:
            if entrada['Tempo'] == tempo:
                entrada['Presenca'] = 0
                break

    def atualizar_entrada(self, p, m, n_quadro, n_pagina):
        self.entradas[n_pagina]['Presenca'] = p
        self.entradas[n_pagina]['Modificacao'] = m
        self.entradas[n_pagina]['Quadro'] = n_quadro
        self.entradas[n_pagina]['Tempo'] = 0

    # mostra o estado atual da TP
    def mostrar(self):
        for item in self.entradas:
            print(item)

    def esvaziar(self):
        self.n_entradas = 0
        self.entradas = []
