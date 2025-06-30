from math import log2
import word as w

class MemoriaPrincipal:
    def __init__(self, qtd_quadros, tam_quadro):
        self.qtd_quadros = qtd_quadros
        self.tam_quadro = tam_quadro
        self.qtd_bits_quadro = int(log2(tam_quadro))

        # enderecado como dados[num_quadro][offset/4]
        # offset/4 pois armazena words, q ocupam 4 bytes
        self.dados: dict[int, list[w.Word]] = {}


    def ler_quadro(self, num_quadro) -> list[w.Word]:
        quadro_copiado = []
        for i in range(self.tam_quadro//4):
            word = self.dados[num_quadro][i]
            quadro_copiado[i] = w.copy_word(word)
        return quadro_copiado


    def escrever_pagina(self, num_quadro, pagina: list[w.Word]):
        if num_quadro < 0 or num_quadro > self.qtd_quadros:
            print("! Tentativa de escrita em endereço ilegal. Abortando.")
            return

        if num_quadro not in self.dados:
            self.dados[num_quadro] = []
        print(f". Escrevendo página no quadro {num_quadro}")
        for idx, word in enumerate(pagina):
            self.dados[num_quadro].append(w.copy_word(word))


    def ler(self, end_fisico) -> w.Word:
        num_quadro, offset = self.desmonta_endereco(end_fisico)
        word = self.dados[num_quadro][(offset//4)]
        return w.copy_word(word)


    def escrever(self, end_fisico, conteudo: w.Word):
        num_quadro, offset = self.desmonta_endereco(end_fisico)
        self.dados[num_quadro][offset//4] = w.copy_word(conteudo)


    def desmonta_endereco(self, endereco_fisico):
        num_quadro = int(bin(endereco_fisico)[:-self.qtd_bits_quadro], 2)
        offset = int(bin(endereco_fisico)[self.qtd_bits_quadro:], 2)
        return num_quadro, offset


    def mostrar(self):
        print("PLACEHOLDER")
