from nucleo_gerenciamento import NucleoGerenciamento


class ProcessadorComandos:
    def __init__(self, nucleo_gerenciamento: NucleoGerenciamento):
        self.nucleo_sistema = nucleo_gerenciamento
        self.contador_ciclos = 0

    def executar_arquivo_instrucoes(self, caminho_arquivo):
        with open(caminho_arquivo) as arquivo_comandos:
            for numero_linha, comando in enumerate(arquivo_comandos):
                print(f"📜 Processando comando {numero_linha + 1}: {comando.strip()}")
                self.processar_comando(comando)
                self.contador_ciclos += 1

    def processar_comando(self, comando: str):
        id_processo, codigo_operacao, parametro_3, parametro_4 = self.analisar_comando(comando)
        print(f"🎯 Tipo de operação identificado: {codigo_operacao}")
        
        if codigo_operacao == "P":
            self.nucleo_sistema.executar_instrucao(id_processo, parametro_3, self.contador_ciclos)
            return
        if codigo_operacao == "I":
            return
        if codigo_operacao == "C":
            self.nucleo_sistema.criar_processo(parametro_3, self.contador_ciclos, id_processo)
            return
        if codigo_operacao == "R":
            self.nucleo_sistema.executar_leitura_memoria(id_processo, parametro_3, self.contador_ciclos)
            return
        if codigo_operacao == "W":
            self.nucleo_sistema.executar_escrita_memoria(id_processo, parametro_3, parametro_4, self.contador_ciclos)
            return
        if codigo_operacao == "T":
            self.nucleo_sistema.finalizar_processo(id_processo, self.contador_ciclos)
            return

    def analisar_comando(self, comando):
        elementos_comando = comando.split()
        id_processo = int(elementos_comando[0].replace("P", ""))
        tipo_operacao = elementos_comando[1]

        if tipo_operacao == "T":
            return id_processo, tipo_operacao, None, None

        if tipo_operacao in ["P", "R", "W", "I"]:
            parametro_3 = int(elementos_comando[2], 2)
        else:
            parametro_3 = int(elementos_comando[2])

        if tipo_operacao != "C" and tipo_operacao != "W":
            return id_processo, tipo_operacao, parametro_3, None
        if tipo_operacao == "C":
            return id_processo, tipo_operacao, self.converter_tamanho(parametro_3, elementos_comando[3]), None
        parametro_escrita = int(elementos_comando[3], 2)
        return id_processo, tipo_operacao, parametro_3, parametro_escrita

    @staticmethod
    def converter_tamanho(quantidade_unidades: int, unidade: str):
        KB = pow(2, 10)
        MB = pow(2, 20)
        GB = pow(2, 30)
        TB = pow(2, 40)

        if unidade == "B":
            return quantidade_unidades
        if unidade == "KB":
            return quantidade_unidades * KB
        if unidade == "MB":
            return quantidade_unidades * MB
        if unidade == "GB":
            return quantidade_unidades * GB
        if unidade == "TB":
            return quantidade_unidades * TB
        raise Exception("⚠️ Erro: Unidade de medida não reconhecida. Máximo suportado: TB") 