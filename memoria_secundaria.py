import word as w

class MemoriaSecundaria:
    def __init__(self, tam_ms, tam_bloco):
        self.tam_ms = tam_ms
        self.tam_bloco = tam_bloco
        self.qtd_blocos = self.tam_ms//self.tam_bloco

        self.dados: dict[int, w.Word] = {}  # endereçado por endereço do bloco + offset
                                            # o offset tendo os 2 últimos bits ignorados,
                                            # pois todos os dados "armazenados" em words

        self.alocados: list[tuple] = [] # [(end_inicial, tam), ...]


    # limitação: o algoritmo utilizado aqui gera fragmentação externa
    def alocar_espaco(self, qtd_paginas) -> int:
        end_candidato = 0
        tam = qtd_paginas * self.tam_bloco

        for alocado in self.alocados:
            if alocado[0] <= end_candidato + tam:
                end_candidato = alocado[0] + alocado[1] + 1
            else:
                self.alocados.append((end_candidato, tam))
                self.tam_ms -= tam
                return end_candidato
        return -1


    def liberar_espaco(self, end_inicial, qtd_paginas):
        tam = qtd_paginas * self.tam_bloco
        end_final = end_inicial + tam

        for end, dado in self.dados.items():
            if end >= end_inicial and end <= end_final:
                self.dados.pop(end)

        self.tam_ms += tam

        for i, alocado in self.alocados:
            # se o espaço a ser removido cobre a alocação toda
            if end_inicial <= alocado[0] and end_final >= alocado[0] + alocado[1]:
                self.alocados.pop(i)
            # um pedaço no começo
            elif end_inicial <= alocado[0] and end_final < alocado[0] + alocado[1]:
                self.alocados.append((end_final + 1, alocado[0] + alocado[1] - end_final))
                self.alocados.pop(i)
            # um pedaço até o final
            elif end_inicial > alocado[0] and end_final >= alocado[0] + alocado[1]:
                alocado[1] = end_inicial - alocado[0]
            # um pedaço no meio
            else:
                if end_inicial > alocado[0] and end_final < alocado[0] + alocado[1]:
                    self.alocados.append((alocado[0], end_inicial - alocado[0]))
                    self.alocados.append((end_final + 1, alocado[0] + alocado[1] - end_final))
                    self.alocados.pop(i)
        self.alocados.sort()


    def ler_bloco(self, end_bloco):
        # deve retornar o bloco todo (obvio)
        bloco_copiado = []

        for i in range(self.tam_bloco):
            word = self.dados[end_bloco + i]
            bloco_copiado.append(self.copy_word(word))

        return bloco_copiado


    def escrever_pagina(self, endereco_bloco, pagina: list[w.Word]):
        for idx, word in enumerate(pagina):
            self.dados[endereco_bloco + idx] = self.copy_word(word)


    def tem_espaco_suficiente(self, qtd_paginas):
        end_candidato = 0
        tam = qtd_paginas * self.tam_bloco

        for alocado in self.alocados:
            if alocado[0] <= end_candidato + tam:
                end_candidato = alocado[0] + alocado[1] + 1
            else:
                return True
        return False


    def copy_word(self, word: w.Word | None) -> w.Word:
        if not word:
            return w.Word().fill_with_trash()

        copied_word = w.Word(word.tipo)
        if word.tipo == w.TipoWord.DADO:
            copied_word.set_dado(word.dado)
        else:
            copied_word.set_instrucao(word.instrucao)
        return copied_word
