from math import log2
import word as w

class MemoriaPrincipal:
    def __init__(self, qtd_quadros, tam_quadro):
        self.qtd_quadros = qtd_quadros
        self.tam_quadro = tam_quadro

        self.qtd_bits_quadro = int(log2(tam_quadro))

        self.dados: dict[int, w.Word] = {}


    def ler_quadro(self, end_fisico) -> dict[int, w.Word]:
        frame_address_part = self._get_frame_addres_part(end_fisico)

        quadro_copiado = {}
        for i in range(0, self.tam_quadro, 4):
            word = self.dados[frame_address_part + i]
            quadro_copiado[i] = w.copy_word(word)
        return quadro_copiado


    def ler(self, end_fisico) -> w.Word:
        word = self.dados[self._get_relevant_address_part(end_fisico)]
        return w.copy_word(word)


    def escrever_pagina(self, end_fisico_pagina, pagina: dict[int, w.Word]):
        for idx, word in pagina.items():
            self.dados[end_fisico_pagina + idx] = w.copy_word(word)


    def escrever(self, end_fisico, conteudo: w.Word):
        self.dados[self._get_relevant_address_part(end_fisico)] = w.copy_word(conteudo)


    def mostrar(self):
        print("PLACEHOLDER")

    # como cada word são 4 bytes, substitui os 2 ultimos bits do endereço por 0
    # pra indexar o dict de dados com offset
    def _get_relevant_address_part(self, physical_address):
        return int(bin(physical_address)[:-2] + '00', 2)

    # pega o endereco sem o offset
    def _get_frame_addres_part(self, physical_address):
        return int(bin(physical_address)[:-self.qtd_bits_quadro] + '0' * self.qtd_bits_quadro, 2)
