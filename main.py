from gerenciador_de_memoria import GerenciadorMemoria
from translation_lookaside_buffer import TLB

from memoria_principal import MemoriaPrincipal
from memoria_secundaria import MemoriaSecundaria
from LeitorDeArquivo import LeitorDeArquivo
from pathlib import Path

from interpreter import Interpreter

def convert_to_bytes(qtd: int, unidade: str):
    match unidade:
        case 'KB':
            return qtd * pow(2, 10)
        case 'MB':
            return qtd * pow(2, 20)
        case 'GB':
            return qtd * pow(2, 30)
    return -1


def main():
    print("Este simulador assume um computador DE 32 bits.")
    print("Assim, a memória principal está limitada a no máximo 4 GiB (4096 MiB), e o endereço lógico pode ter no máximo 32 bits.")
    print("Valores maiores que os indicados acima serão ignorados, setados automaticamente para os limites.")

    # tam_quadro = int(input("Defina o tamanho do quadro/página:"))
    # tam_end_logico = int(input("Digite o tamanho em bits do endereço lógico:"))
    # n_entrada_tlb = int(input("Digite o numero de entradas da TLB:"))
    # entrada_tam_mp = input("Digite o tamanho da memoria principal seguido da unidade (qtd KB|MB|GB):")
    # entrada_tam_mem_sec = input("Digite o tamanho da memoria secundaria para swap, seguido da unidade (qtd KB|MB|GB):")

    # teste
    tam_quadro = 4096
    tam_end_logico = 32
    n_entrada_tlb = 64
    entrada_tam_mp = "2 GB"
    entrada_tam_mem_sec = "2 GB"

    tam, unidade = entrada_tam_mp.split(' ')
    tam_mp = convert_to_bytes(int(tam), unidade)

    tam, unidade = entrada_tam_mem_sec.split(' ')
    tam_mem_sec = convert_to_bytes(int(tam), unidade)

    if tam_end_logico > 32:
        tam_end_logico = 32
    if tam_mp > 4 * pow(2,30):
        tam_mp = 4 * pow(2,30)

    print("Aguarde um tempo, essa operação pode demorar")

    n_quadro = tam_mp // tam_quadro

    tlb = TLB(n_entrada_tlb)
    mem_principal = MemoriaPrincipal(n_quadro, tam_quadro)
    mem_sec = MemoriaSecundaria(tam_mem_sec, tam_quadro)
    gm = GerenciadorMemoria(tlb, mem_principal, mem_sec, tam_end_logico, tam_quadro, 'LRU')

    caminho_arquivo = Path("entrada.txt")
    leitor = LeitorDeArquivo()
    programa = leitor.carregar_arquivo(caminho_arquivo)

    interpreter = Interpreter(programa, gm)
    interpreter.start()

if __name__ == "__main__":
    main()
