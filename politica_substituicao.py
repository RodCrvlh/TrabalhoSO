# LEGACY
class PoliticaSubstituicao:
    @staticmethod
    def lru_tp(tp, mp, ms, id_processo, n_pagina, m):

        maior_tempo = -1
        idx_maior = -1

        for idx, entrada in enumerate(tp.entradas):
            if entrada['Tempo'] > maior_tempo:
                maior_tempo = entrada['Tempo']
                idx_maior = idx

        entrada_subs = tp.entradas[idx_maior]  # pega entrada que será substituida por ter mais tempo sem ser executada

        tp.retirar_presenca(maior_tempo)

        quadro = mp.ler(entrada_subs['Quadro'])  # pegar quadro antigo da Mp
        mp.liberar_quadro(entrada_subs['Quadro'])  # libera o quadro da MP
        novo_quadro = ms.carregar(id_processo, n_pagina)  # carregar pagina desejada em um novo quadro
        ms.salvar(quadro['Processo'], 1, quadro['Conteudo'])  # salvar quadro antigo na MS

        if novo_quadro is None:  # verifica se página existe
            return None

        n_novo_quadro = mp.alocar_quadro(id_processo, n_pagina, novo_quadro['Conteudo'])
        tp.atualizar(1, m, n_novo_quadro, n_pagina)
        tp.atualizar(0, 0, -1, idx_maior)

        return n_novo_quadro

    @staticmethod
    def lru_tlb(tlb, mp, n_quadro, m):
        maior_tempo = 0
        for entrada in tlb.entradas:
            if entrada['Tempo'] > maior_tempo:
                maior_tempo = entrada['Tempo']

        tlb.retirar_presenca(maior_tempo)  # pega entrada que será substituida por ter mais tempo sem ser executada

        quadro = mp.ler(n_quadro)
        tlb.atualizar(quadro['Pagina'], 1, m, n_quadro)

    @staticmethod
    def relogio(entradas):
        print(entradas)

    def sub_tp(self, tabela, mp, ms, id_processo, bits_pagina, m):

        print("Falta de Pagina!")

        while True:

            print("Escolha 1 para LRU e 2 para Relógio")
            op = int(input())

            if op == 1:
                return self.lru_tp(tabela, mp, ms, id_processo, bits_pagina, m)
            elif op == 2:
                return self.relogio(tabela)
            else:
                print("Digite as opções 1 ou 2!")

    def sub_tlb(self, tabela, mp, n_quadro, m):

        print("TLB miss")

        while True:

            print("Escolha 1 para LRU e 2 para Relógio")
            op = int(input())

            if op == 1:
                return self.lru_tlb(tabela, mp, n_quadro, m)
            elif op == 2:
                return self.relogio(tabela)
            else:
                print("Digite as opções 1 ou 2!")
