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
            }
            entradas.append(entrada)
        return entradas


    def adicionar_pagina(self, num_pagina, num_quadro):
        entrada = self.entradas[num_pagina]
        entrada["Presenca"] = 1
        entrada["Quadro"] = num_quadro


    def buscar_quadro(self, n_pagina):
        if self.entradas[n_pagina]['Presenca'] == 1:  # Achou a pagina na TP
            return self.entradas[n_pagina]['Quadro']
        return -1 # Não achou pagina na TP


    def atualizar_entrada(self, p, m, n_quadro, n_pagina):
        self.entradas[n_pagina]['Presenca'] = p
        self.entradas[n_pagina]['Modificacao'] = m
        self.entradas[n_pagina]['Quadro'] = n_quadro


    # mostra o estado atual da TP
    def mostrar(self):
        for item in self.entradas:
            print(item)


    def esvaziar(self):
        self.n_entradas = 0
        self.entradas = []
