
class MemoriaPrincipal:
    def __init__(self, qtd_quadros, tam_quadro):
        self.qtd_quadros = qtd_quadros
        self.tam_quadro = tam_quadro
        self.quadros = self.init_quadros()

        self.quadros_livres = [i for i in range(qtd_quadros)]


    def init_quadros(self):
        quadros = []
        for _ in range(self.qtd_quadros):
            quadro = [""] * self.tam_quadro
            quadros.append(quadro)

        return quadros


    def esta_cheio(self):
        return len(self.quadros_livres) == 0


    def ler(self, n_quadro):
        return self.quadros[n_quadro]


    def escrever(self, n_quadro, offset, conteudo):
        if n_quadro >= self.qtd_quadros:
            print("Endereço invalido")
            return

        self.quadros[n_quadro][offset] = conteudo


    def escrever_pagina(self, n_quadro, pagina):
        if n_quadro >= self.qtd_quadros:
            print("Endereço invalido")
            return

        self.quadros[n_quadro] = pagina


    def alocar_quadro(self):
        if self.esta_cheio():
            return -1

        end_quadro = self.quadros_livres.pop(0)
        return end_quadro


    def liberar_quadro(self, id_quadro):
        if id_quadro >= self.qtd_quadros:
            print("Quadro inexistente")
            return

        self.quadros_livres.append(id_quadro)


    def mostrar(self):
        print("Memoria Principal:")
        print("------------------------------------")
        for i, quadro in enumerate(self.quadros):
            if quadro['Processo'] == -1:
                print(f"Quadro {i}: Livre")
            else:
                print(f"Quadro {i}: Processo{quadro['Processo']}, Pagina:{quadro['Pagina']}, "
                      f"Conteudo:{quadro['Conteudo']}")
        print("------------------------------------")
