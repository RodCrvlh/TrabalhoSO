import copy

class MemoriaSecundaria:
    def __init__(self, tam_ms, tam_pagina):
        self.tam_ms = tam_ms
        self.tam_pagina = tam_pagina
        self.qtd_blocos = self.tam_ms//self.tam_pagina
        self.dados = self.init_dados()

        # define onde tem espaço livre
        # 0 pra vazio, 1 pra usado
        self.blocos_bitmap = '0' * self.qtd_blocos


    def init_dados(self):
        dados = []
        for _ in range(self.qtd_blocos):
            dado = [""] * self.tam_pagina
            dados.append(dado)
        return dados


    def alocar_espaco(self, qtd_paginas):
        end_inicial = self.blocos_bitmap.find('0' * qtd_paginas)

        if end_inicial == -1:
            return -1

        for i in range(end_inicial, end_inicial + qtd_paginas):
            self.blocos_bitmap[i] = 0
        return end_inicial


    def liberar_espaco(self, end_inicial, page_count):
        for idx in range(end_inicial, end_inicial + page_count):
            self.blocos_bitmap[idx] = '0'


    def ler_bloco(self, end_pagina):
       return copy.deepcopy(self.dados[end_pagina])


    def escrever_pagina(self, endereco_bloco, pagina):
        self.dados[endereco_bloco] = copy.deepcopy(pagina)


    # limitação: checa apenas se tem espaço contíguo. MS sujeita a fragmentação externa
    def tem_espaco_suficiente(self, qtd_paginas):
        if self.blocos_bitmap.find('0' * qtd_paginas) > -1:
            return True
        return False


    # def mostrar(self):
    #     print("-------------------------------")
    #     print("Memoria Secundaria")

    #     for i, dado in enumerate(self.dados):
    #         if dado['Pagina'] == -1:
    #             print(f"Espaço{i}: Livre")
    #         else:
    #             print(f"Espaço {i}: Pagina {dado['Pagina']}, Processo {dado['Processo']}, Conteudo:{dado['Conteudo']}")

    #     print("--------------------------------")
