class MemoriaPrincipal:
    def __init__(self, qtd_quadros, tam_quadro):
        self.qtd_quadros = qtd_quadros
        self.tam_quadro = tam_quadro
        self.quadros = self.init_quadros()


    def init_quadros(self):
        quadros = []
        for _ in range(self.qtd_quadros):
            quadro = [""] * self.tam_quadro
            quadros.append(quadro)
        return quadros


    def ler_quadro(self, num_quadro):
        return self.quadros[num_quadro]


    def ler(self, num_quadro, offset):
        return self.quadros[num_quadro][offset]


    def escrever_pagina(self, num_quadro, pagina):
        if num_quadro >= self.qtd_quadros:
            print("Endereço invalido")
            return
        self.quadros[num_quadro] = pagina


    def escrever(self, num_quadro, offset, conteudo):
        if num_quadro >= self.qtd_quadros:
            print("Endereço invalido")
            return
        self.quadros[num_quadro][offset] = conteudo


    def mostrar(self):
        print("PLACEHOLDER")
