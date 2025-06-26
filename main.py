import math

from gerenciador_memoria import GerenciadorMemoria
from translation_lookaside_buffer import TLB

from memoria_principal import MemoriaPrincipal
from memoria_secundaria import MemoriaSecundaria


def main():
    tam_quadro = int(input("Defina o tamanho do quadro/página:"))
    tam_end_logico = int(input("Digite o tamanho em bits do endereço lógico:"))
    n_entrada_tlb = int(input("Digite o numero de entradas da TLB:"))
    tam_mp = int(input("Digite o tamanho da memoria principal:"))
    tam_mem_sec = int(input("Digite o tamanho da memoria secundaria:"))

    n_entrada_tp = int(math.pow(2, tam_end_logico))//tam_quadro
    n_quadro = tam_mp // tam_quadro

    tlb = TLB(n_entrada_tlb)
    mem_principal = MemoriaPrincipal(n_quadro, tam_quadro)
    mem_sec = MemoriaSecundaria(tam_mem_sec, tam_quadro)
    gm = GerenciadorMemoria(tlb, mem_principal, mem_sec, tam_end_logico)

    while True:
        print("-------------------------------------------------")
        print("Bem vindo ao simulador de Gerenciador de Memoria! Digte a letra referente a opcao.")
        print("P - intrução a ser executada pela CPU (sem ser leitura ou escrita")
        print("I - instrução de I/O")
        print("C - criação (submissão de processos")
        print("R - pedido de leitura executado pela CPU em um endereço lógico")
        print("W - pedido de escrita executado pela CPU em um endereço lógico de um valor")
        print("T - terminação processo")
        print("-------------------------------------------------")

        opcao = input()

        if opcao == 'P':
            print("Opcao não implementada ainda")

        elif opcao == 'I':
            print("Opcao não implementada ainda")

        elif opcao == 'C':
            tamanho = int(input("Digite o tamanho do processo:"))
            gm.criar_processo(n_entrada_tp, tamanho)

        elif opcao == 'R':
            id_processo = int(input("Digite o id do processo:"))
            end_logico = int(input("Digite o endereço logico:"))
            leitura = gm.leitura_memoria(id_processo, end_logico)

            if leitura is not None:
                print(leitura)

        elif opcao == 'W':
            id_processo = int(input("Digite o id do processo:"))
            end_logico = int(input("Digite o endereço logico:"))
            conteudo = str(input("Digite o conteudo que deseja amarzenar:"))
            gm.escrita_memoria(id_processo, end_logico, conteudo)

        elif opcao == 'T':
            id_processo = int(input("Digite o id do processo"))
            gm.terminar_processo(id_processo)

        else:
            print("Digite um numero referente as opcoes.")


if __name__ == "__main__":
    main()
