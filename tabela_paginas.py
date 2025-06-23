class TP:
    # inicializa a Tabela de Paginas
    def __init__(self, n_entradas):
        self.n_entradas = n_entradas
        self.entradas = self.init_entradas()

    # inicializa o dicionario entradas que representa as entradas da TP
    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Presenca':  0,
                'Modificacao': 0,
                'Quadro': -1,
                'Tempo': 0
                # O tempo serve para politica LRU, significa quantas buscas foram feitas sem ele ser acessado
            }
            entradas.append(entrada)
        return entradas

    def aumentar_tempo(self, n_pagina):
        print(f"pg:{n_pagina}")
        print(f"n_entradas:{self.n_entradas}")
        for i in range(self.n_entradas):
            if i != n_pagina and self.entradas[i]['Quadro'] != -1:
                print(self.entradas[i]['Tempo'])
                self.entradas[i]['Tempo'] += 1

    # busca na TP em que quadro uma pagina esta amarzenada
    def buscar(self, n_pagina, mp):

        if self.entradas[n_pagina]['Presenca'] == 1:  # Achou a pagina na TP
            self.entradas[n_pagina]['Tempo'] = 0
            self.aumentar_tempo(n_pagina)
            return self.entradas[n_pagina]['Quadro']

        elif self.entradas[n_pagina]['Quadro'] == -1:  # Não achou a pagina na TP

            if not mp.esta_cheio():  # Verifica que é possível adicionar a página na TP
                self.aumentar_tempo(n_pagina)
                return -2

            else:  # Verifica que não é possível adicionar a página na TP
                self.aumentar_tempo(n_pagina)
                return -1

    def retirar_presenca(self, tempo):
        for entrada in self.entradas:
            if entrada['Tempo'] == tempo:
                entrada['Presenca'] = 0
                break

    # atualiza uma entrada da TP
    def atualizar(self, p, m, n_quadro, n_pagina):
        self.entradas[n_pagina]['Presenca'] = p
        self.entradas[n_pagina]['Modificacao'] = m
        self.entradas[n_pagina]['Quadro'] = n_quadro
        self.entradas[n_pagina]['Tempo'] = 0

    # mostra o estado atual da TP
    def mostrar(self):
        for item in self.entradas:
            print(item)
