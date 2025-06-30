from gerenciador_de_memoria import GerenciadorMemoria
from instrucao_processo import InstrucaoProcesso

class Interpreter:
    def __init__(self, programa: list[str], gm: GerenciadorMemoria):
        self.gm = gm
        self.programa = programa


    def start(self):
        self.interpret()
        self.run()

    def interpret(self):
        for instrucao in self.programa:
            partes = instrucao.split() # divide a linha em várias strings

            id_processo = partes[0]
            operacao = partes[1]

            if operacao == 'C':
                tamanho = self.get_tamanho_em_bytes(int(partes[2]), partes[3])
                self.gm.criar_processo(id_processo, tamanho)
            else:
                instrucao_processo = InstrucaoProcesso(id_processo, operacao, int(partes[2]) if len(partes) > 2 else 0, int(partes[3]) if len(partes) > 3 else 0)
                self.gm.adicionar_instrucao_processo(id_processo, instrucao_processo)


    def run(self):
        while self.gm.ready_queue_head or self.gm.blocked_queue_head:
            processo_atual = self.gm.ready_queue_head

            if processo_atual:
                self.gm.set_process_running(processo_atual)
                instrucao = processo_atual.instrucoes_simuladas[processo_atual.pc]

                if instrucao.operacao == 'R':
                    self.gm.solicita_leitura_memoria(instrucao.id_processo, instrucao.endereco_logico)
                if instrucao.operacao == 'W':
                    self.gm.solicita_escrita_memoria(instrucao.id_processo, instrucao.endereco_logico, instrucao.valor)
                if instrucao.operacao == 'P':
                    self.gm.executar_instrucao_cpu(instrucao.id_processo, instrucao.endereco_logico)
                if instrucao.operacao == 'I':
                    # aqui não usa realmente o endereco logico, só foi mapeado pro mesmo campo
                    self.gm.executar_operacao_io(instrucao.id_processo, instrucao.endereco_logico)
                if instrucao.operacao == 'T':
                    self.gm.terminar_processo(instrucao.id_processo)


    def get_tamanho_em_bytes(self, num, sufixo):
        match sufixo:
            case 'KB':
                return num * pow(2, 10)
            case 'MB':
                return num * pow(2, 20)
            case 'GB':
                return num * pow(2, 30)
