import copy

# Estrutura que mantem as paginas que não estão na memoria principal

class MemoriaSecundaria:
    def __init__(self, tam_ms, tam_pagina):
        self.tam_ms = tam_ms
        self.tam_pg = tam_pagina
        self.dados = self.init_dados()

    def init_dados(self):
        dados = []
        tam_espaco = self.tam_ms//self.tam_pg
        for _ in range(tam_espaco):
            dado = {
                'Conteudo': [""] * self.tam_pg,
                'Processo': -1,  # qual processo essa pagina pertence
                'Pagina': -1     # numero da pagina dentro do processo
            }
            dados.append(dado)
        return dados

    def liberar_processo(self, id_processo):
        for i, dado in enumerate(self.dados):
            if dado['Processo'] == id_processo:
                self.dados[i] = {
                    'Conteudo': [""]*self.tam_pg,
                    'Processo': -1,
                    'Pagina': -1
                }

    def carregar(self, id_processo, n_pagina):
        for i, dado in enumerate(self.dados):
            if int(dado['Processo']) == id_processo and dado['Pagina'] == n_pagina:
                novo_quadro = copy.deepcopy(dado)  # cria uma cópia do dado que não referencia o seu endereço original
                self.dados[i]['Conteudo'] = [""] * self.tam_pg
                self.dados[i]['Processo'] = -1
                self.dados[i]['Pagina'] = -1
                return novo_quadro

        print(f"Pagina {n_pagina} do processo {id_processo} não está na Memória Secundária")
        return None

    def salvar(self, id_processo, n_paginas, conteudo):

        for idx, dado in enumerate(self.dados):
            if dado['Processo'] == -1:
                self.dados[idx] = {
                    'Conteudo': conteudo,
                    'Processo': id_processo,
                    'Pagina': idx
                }
                n_paginas -= 1

            if n_paginas == 0:
                return True

        print(n_paginas)
        print("Espaço insuficiente na Memoria Secundaria ")
        return False

    def mostrar(self):
        print("-------------------------------")
        print("Memoria Secundaria")

        for i, dado in enumerate(self.dados):
            if dado['Pagina'] == -1:
                print(f"Espaço{i}: Livre")
            else:
                print(f"Espaço {i}: Pagina {dado['Pagina']}, Processo {dado['Processo']}, Conteudo:{dado['Conteudo']}")

        print("--------------------------------")
