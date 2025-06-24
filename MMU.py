import math

class MMU:
    def __init__(self, tam_end_logico, tam_quadro):
        self.end_logico = self.init_end_logico(tam_end_logico)
        self.tam_quadro = tam_quadro


    def init_end_logico(self, tam_end_logico):
        tam_pg = self.tam_quadro  # tamanho da pg = tamanho do quadro
        offset_bits = int(math.log(tam_pg, 2))  # pega o numero de bits para offset
        n_pagina_bits = int(tam_end_logico-offset_bits)

        end_logico = {
            '#Pagina': n_pagina_bits,
            'offset': offset_bits
        }
        return end_logico


    def traduzir_endereco(self, end_logico):
        end_fisico = bin(end_logico)[2:].zfill(16)   # remove prefixo '0b'e preenche com zeros a esquerda
        bits_pagina = self.end_logico['#Pagina']
        n_pagina = int(end_fisico[:bits_pagina], 2)
        offset = int(end_fisico[bits_pagina:self.end_logico['offset']], 2)
        return n_pagina, offset
