from typing import List
from math import ceil
from sistema_logging import SistemaLogging


class ElementoMemoria:
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.ocupado = False
        self.dados = bytearray([0 for i in range(tamanho)])


class UnidadePagina:
    def __init__(self, numero_frame: int, identificador_pagina: int, identificador_processo: int):
        self.numero_frame = numero_frame
        self.presente_memoria_principal = False
        self.modificada = False
        self.timestamp_ultimo_acesso = 0
        self.identificador_pagina = identificador_pagina
        self.identificador_processo = identificador_processo


class ColecaoPaginasProcesso:
    def __init__(self):
        self.conjunto_paginas: List[UnidadePagina] = []

    def inicializar_paginas(self, tamanho_processo: int, tamanho_pagina: int, id_processo):
        quantidade_paginas = ceil(tamanho_processo / tamanho_pagina)
        for indice_pagina in range(quantidade_paginas):
            SistemaLogging.registrar(f"▶ Criando página {indice_pagina} na tabela de páginas do processo")
            self.conjunto_paginas.append(UnidadePagina(0, indice_pagina, id_processo))

    def remover_pagina(self, pagina):
        self.conjunto_paginas.remove(pagina)

    def remover_pagina_por_indice(self, numero_pagina):
        self.conjunto_paginas.pop(numero_pagina) 