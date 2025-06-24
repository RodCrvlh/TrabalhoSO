class TLB:
    # inicializa a TLB
    def __init__(self, n_entradas):
        self.n_entradas = n_entradas
        self.entradas = self.init_entradas()

    # inicializa o dicionario entradas que representa as entradas da TLB
    def init_entradas(self):
        entradas = []
        for _ in range(self.n_entradas):
            entrada = {
                'Validade': 0,
                'Pagina': -1,
                'Presenca': 0,
                'Modificacao': 0,
                'Quadro': -1,
            }
            entradas.append(entrada)
        return entradas


    def buscar(self, n_pagina):
        for i, entrada in enumerate(self.entradas):
            if entrada['Validade'] == 1 and entrada['Pagina'] == n_pagina: # entrada encontrada
                return self.entradas[i]['Quadro']

        return -1 # entrada não encontrada


    def ta_cheio(self):
        return any(entrada["Validade"] == 0 and entrada["Quadro"] != -1 for entrada in self.entradas)


    def retirar_presenca(self, tempo):
        for entrada in self.entradas:
            if entrada['Tempo'] == tempo:
                entrada['Presenca'] = 0
                break

    # Atualiza uma entrada da TLB
    # Prec
    def atualizar(self, n_pagina, v, m, n_quadro):
        for entrada in self.entradas:
            if entrada['Presenca'] == 0:
                entrada['Presenca'] = 1
                entrada['Validade'] = v
                entrada['Pagina'] = n_pagina
                entrada['Modificacao'] = m
                entrada['Quadro'] = n_quadro
                entrada['Tempo'] = 0
                break

    def mostrar(self):
        for item in self.entradas:
            print(item)
