from typing import Optional, List

class TLBEntry:
    def __init__(self, indice: int):
        self.validade: int = 0
        self.pagina: int = -1
        self.presenca: int = 0
        self.modificacao: int = 0
        self.quadro: int = -1
        self.tempo: int = 0
        self.indice: int = indice

    def is_valid(self) -> bool:
        return self.validade == 1

    def is_present(self) -> bool:
        return self.presenca == 1

    def is_modified(self) -> bool:
        return self.modificacao == 1

    def matches_page(self, n_pagina: int) -> bool:
        return self.is_valid() and self.pagina == n_pagina

    def clear(self):
        self.validade = 0
        self.pagina = -1
        self.presenca = 0
        self.modificacao = 0
        self.quadro = -1
        self.tempo = 0

    def update(self, n_pagina: int, v: int, m: int, n_quadro: int, tempo: int):
        self.validade = v
        self.pagina = n_pagina
        self.presenca = 1
        self.modificacao = m
        self.quadro = n_quadro
        self.tempo = tempo

    def __str__(self) -> str:
        return (f"Entry[{self.indice}]: Valid={self.validade}, "
                f"Page={self.pagina}, Present={self.presenca}, "
                f"Modified={self.modificacao}, Frame={self.quadro}, "
                f"Time={self.tempo}")

    def __repr__(self) -> str:
        return self.__str__()


class TLB:
    def __init__(self, n_entradas: int):
        self.n_entradas = n_entradas
        self.entradas: List[TLBEntry] = self.init_entradas()
        self.acessos = 0  # pra LRU
        self.hits = 0
        self.misses = 0

    def init_entradas(self) -> List[TLBEntry]:
        return [TLBEntry(i) for i in range(self.n_entradas)]

    def buscar(self, n_pagina: int) -> int:
        self.acessos += 1

        for entrada in self.entradas:
            if entrada.matches_page(n_pagina):
                # TLB Hit
                entrada.tempo = self.acessos
                self.hits += 1
                return entrada.quadro

        # TLB Miss
        self.misses += 1
        return -1

    def ta_cheio(self) -> bool:
        return all(entrada.is_valid() for entrada in self.entradas)

    def encontrar_entrada_livre(self) -> Optional[int]:
        for i, entrada in enumerate(self.entradas):
            if not entrada.is_valid():
                return i
        return None

    def encontrar_entrada_substituir_LRU(self) -> int:
        min_tempo = min(entrada.tempo for entrada in self.entradas)
        for i, entrada in enumerate(self.entradas):
            if entrada.tempo == min_tempo:
                return i
        return 0  # primeira entrada padrão

    def retirar_presenca(self, n_pagina: int):
        for entrada in self.entradas:
            if entrada.matches_page(n_pagina):
                entrada.presenca = 0
                break

    def invalidar_entrada(self, n_pagina: int):
        for entrada in self.entradas:
            if entrada.matches_page(n_pagina):
                entrada.clear()
                break

    def atualizar(self, n_pagina: int, v: int, m: int, n_quadro: int):
        self.acessos += 1

        # vê se página já existe
        for entrada in self.entradas:
            if entrada.matches_page(n_pagina):
                # atualiza a que já existe
                entrada.presenca = 1
                entrada.modificacao = m
                entrada.quadro = n_quadro
                entrada.tempo = self.acessos
                return

        # acha uma entrada vazia ou substitui
        entrada_idx = self.encontrar_entrada_livre()
        if entrada_idx is None:
            entrada_idx = self.encontrar_entrada_substituir_LRU()

        # atualiza entrada
        self.entradas[entrada_idx].update(n_pagina, v, m, n_quadro, self.acessos)

    def flush(self):
        for entrada in self.entradas:
            entrada.clear()
        self.acessos = 0
        self.hits = 0
        self.misses = 0

    def get_entry(self, index: int) -> Optional[TLBEntry]:
        if 0 <= index < self.n_entradas:
            return self.entradas[index]
        return None

    def get_valid_entries(self) -> List[TLBEntry]:
        return [entrada for entrada in self.entradas if entrada.is_valid()]


    def mostrar(self):
        print(f"\n--- TLB Status ({self.n_entradas} entries ---")
        print("Idx | Valid | Page | Present | Modified | Frame | Time")
        print("-" * 55)

        for entrada in self.entradas:
            print(f"{entrada.indice:2d}  |   {entrada.validade}   | {entrada.pagina:4d} |    {entrada.presenca}    |    {entrada.modificacao}     | {entrada.quadro:4d}  | {entrada.tempo:4d}")


    def mostrar_entrada(self, index: int):
        entrada = self.get_entry(index)
        if entrada:
            print(entrada)
        else:
            print(f"index invalido: {index}")


    def find_page(self, n_pagina: int) -> Optional[TLBEntry]:
        for entrada in self.entradas:
            if entrada.matches_page(n_pagina):
                return entrada
        return None
