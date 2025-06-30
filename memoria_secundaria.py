from curses import has_key
from math import log2
import threading
from typing import Callable
import word as w

from tipo_interrupt import TipoInterrupt

class MemoriaSecundaria:
    def __init__(self, tam_ms, tam_bloco):
        self.tam_ms = tam_ms

        self.tam_bloco = tam_bloco
        self.qtd_blocos = self.tam_ms//self.tam_bloco
        self.qtd_bits_bloco = int(log2(self.tam_bloco))

        # enderecado como dados[num_bloco][offset/4]
        # offset/4 pois armazena words, q ocupam 4 bytes
        self.dados: dict[int, list[w.Word]] = {}

        self.blocos_livres: list[int] = [i for i in range(self.qtd_blocos)]

    def alocar_bloco(self):
        if len(self.blocos_livres) <= 0:
            return -1
        return self.blocos_livres.pop()


    def liberar_bloco(self, num_bloco) -> bool:
        if num_bloco < 0 or num_bloco >= self.qtd_blocos:
            print(f"Bloco {num_bloco} da MS não existe")
            return False
        self.blocos_livres.append(num_bloco)
        print(f"Bloco {num_bloco} da MS foi liberado")
        return True


    def ler_bloco(self, swap_block_num, process_id, num_pagina, interrupt_handler: Callable[[TipoInterrupt, str, int, list[w.Word] | None], None]):
        bloco_copiado = []
        for i in range(self.tam_bloco//4):
            word = self.dados[swap_block_num][i] if swap_block_num in self.dados else None
            bloco_copiado.append(w.copy_word(word))
        threading.Timer(2, interrupt_handler, args=(TipoInterrupt.LEITURA_MS, process_id, num_pagina, bloco_copiado))


    def escrever_pagina(self, swap_block_num, pagina: list[w.Word]):
        for idx, word in enumerate(pagina):
            self.dados[swap_block_num][idx] = w.copy_word(word)


    def finge_que_ta_pegando_do_arquivo(self, num_pagina, process_id, interrupt_handler: Callable[[TipoInterrupt, str, int,  list[w.Word] | None], None]):
        print("∟ ...carregando a página no arquivo original...")
        bloco_lido = []
        for i in range(self.tam_bloco//4):
            word = w.copy_word()
            bloco_lido.append(word)

        timer = threading.Timer(2, interrupt_handler, args=(TipoInterrupt.LEITURA_MS, process_id, num_pagina, bloco_lido))
        timer.start()


    def desmonta_endereco(self, endereco_fisico):
        num_quadro = int(bin(endereco_fisico)[:-self.qtd_bits_bloco], 2)
        offset = int(bin(endereco_fisico)[self.qtd_bits_bloco:], 2)
        return num_quadro, offset


    def tem_espaco_suficiente(self, qtd_paginas):
        if len(self.blocos_livres) > qtd_paginas:
            return False
        return True
