import math

from translation_lookaside_buffer import TLB
from page_table import PageTable

class EnderecoLogico:
    def __init__(self, num_pagina, offset):
        self.num_pagina = num_pagina
        self.offset = offset

    def num_pag_int(self) -> int:
        return int(self.num_pagina, 2)

    def offset_int(self) -> int:
        return int(self.offset, 2)


class MemoryManagementUnit:
    # tam_end_logico -> em bits
    # tam_quadro -> define a quantidade de bits do offset
    def __init__(self, tlb: TLB, tam_end_logico: int, tam_quadro: int):
        self.tlb: TLB = tlb

        self.tam_end_logico = tam_end_logico
        self.tam_quadro = tam_quadro

        self.qtd_bits_offset = int(math.log(tam_quadro, 2))
        self.qtd_bits_num_pag = tam_end_logico - self.qtd_bits_offset


    def buscar_pagina(self, end_logico: EnderecoLogico, page_table_base: PageTable) -> int:
        # procura se a pagina esta na tlb
        num_quadro_tlb = self.tlb.buscar(end_logico.num_pag_int())
        if num_quadro_tlb != -1:
            print("TLB hit!")
            return num_quadro_tlb

        # se TLB miss, faz table walk:
        # no caso, procura apenas na única camada da page table
        num_quadro_tp = page_table_base.buscar_quadro(end_logico.num_pag_int())

        if num_quadro_tp != -1:
            print("TP hit!")
            return num_quadro_tp

        # se não achou nem na tlb nem na tp, page fault:
        return -1


    def create_end_logico_bin(self, endereco_logico_decimal: int):
        # remove prefixo '0b'e preenche com zeros a esquerda
        end_logico_bin = bin(endereco_logico_decimal)[2:].zfill(self.tam_end_logico)
        bits_num_pagina = end_logico_bin[:self.qtd_bits_num_pag]
        bits_offset = end_logico_bin[:-self.qtd_bits_offset]

        return EnderecoLogico(bits_num_pagina, bits_offset)


    def traduzir_endereco(self, end_logico: EnderecoLogico, num_quadro_dec: int) -> int:
        num_quadro_bin = bin(num_quadro_dec)[2:].zfill(self.qtd_bits_num_pag)
        end_fisico = num_quadro_bin + end_logico.offset
        return int(end_fisico, 2)
