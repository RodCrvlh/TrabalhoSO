import word as w

class MemoriaPrincipal:
    def __init__(self, qtd_quadros, tam_quadro):
        self.qtd_quadros = qtd_quadros
        self.tam_quadro = tam_quadro

        self.dados: dict[int, w.Word] = {}


    def ler_quadro(self, end_fisico) -> list[w.Word]:
        # deve retornar o qudro todo (obvio)
        quadro_copiado = []

        for i in range(self.tam_quadro):
            # TODO: might be wrong
            word = self.dados[end_fisico + i]
            quadro_copiado.append(w.copy_word(word))

        return quadro_copiado


    def ler(self, end_fisico) -> w.Word:
        word = self.dados[end_fisico]
        return w.copy_word(word)


    def escrever_pagina(self, end_fisico_pagina, pagina: list[w.Word]):
        for idx, word in enumerate(pagina):
            self.dados[end_fisico_pagina + idx] = w.copy_word(word)


    def escrever(self, end_fisico, conteudo: w.Word):
        self.dados[end_fisico] = w.copy_word(conteudo)


    def mostrar(self):
        print("PLACEHOLDER")
