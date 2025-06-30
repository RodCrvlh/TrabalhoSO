class InstrucaoProcesso:
    def __init__(self, id_processo: str, operacao: str, endereco_logico: int, valor: int):
        self.id_processo = id_processo
        self.operacao = operacao
        self.endereco_logico = endereco_logico
        self.valor = valor
