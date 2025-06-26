from enum import Enum
from math import ceil
from typing import List
from sistema_paginacao import ColecaoPaginasProcesso
from configuracoes import tamanho_pagina


class EstadoProcesso(Enum):
    INICIALIZADO = 0
    AGUARDANDO = 1
    BLOQUEADO = 2
    EM_EXECUCAO = 3
    TERMINADO = 4
    AGUARDANDO_SUSPENSO = 5
    BLOQUEADO_SUSPENSO = 6


class EntidadeProcesso:
    def __init__(self, identificador_processo: int, tamanho_total: int, tamanho_pagina):
        self.identificador = identificador_processo
        self.tamanho_total = tamanho_total
        self.estado_atual = EstadoProcesso.INICIALIZADO
        self.historico_operacoes: List[str] = []
        self.gerenciador_paginas = ColecaoPaginasProcesso()
        self.gerenciador_paginas.inicializar_paginas(tamanho_total, tamanho_pagina, identificador_processo)

    def finalizar_processo(self):
        self.estado_atual = EstadoProcesso.TERMINADO
        self.tamanho_total = 0

    def obter_paginas(self):
        return self.gerenciador_paginas.conjunto_paginas

    def calcular_pagina_e_offset(self, endereco_logico):
        numero_pagina = endereco_logico // tamanho_pagina
        offset = endereco_logico % tamanho_pagina
        if not self.validar_endereco(endereco_logico):
            pass
        return {"pagina": numero_pagina, "offset": offset}

    def validar_endereco(self, endereco_logico):
        if endereco_logico < 0:
            raise Exception("⚠️ Erro crítico: Endereço com valor negativo não é permitido.")

        quantidade_paginas = ceil(self.tamanho_total / tamanho_pagina)
        pagina_correspondente = endereco_logico // tamanho_pagina
        offset_correspondente = endereco_logico % tamanho_pagina
        ultima_pagina_valida = quantidade_paginas - 1

        if pagina_correspondente > ultima_pagina_valida:
            raise Exception(f"⚠️ Violação de memória detectada: Tentativa de acesso a página inexistente.\n"
                            f"📍 Página solicitada: {pagina_correspondente} | Offset: {offset_correspondente} | Endereço: {endereco_logico}")

        espaco_nao_utilizado = (quantidade_paginas * tamanho_pagina) - self.tamanho_total
        maior_offset_valido = tamanho_pagina - espaco_nao_utilizado - 1
        if pagina_correspondente == ultima_pagina_valida and offset_correspondente > maior_offset_valido:
            raise Exception("⚠️ Acesso inválido: Tentativa de acesso à região não alocada da última página.\n"
                            f"📍 Página: {pagina_correspondente} | Offset: {offset_correspondente} | Endereço: {endereco_logico}")
        return True


class RegistroProcessos:
    def __init__(self, tamanho_pagina):
        self.tamanho_pagina = tamanho_pagina
        self.proximo_id_disponivel = 0
        self.processos_ativos: List[EntidadeProcesso] = []
        self.processos_finalizados: List[EntidadeProcesso] = []
        self.identificadores_em_uso = set()

    def criar_novo_processo(self, tamanho_processo, id_personalizado=None):
        identificador_final = self.gerar_identificador(id_personalizado)
        self.processos_ativos.append(EntidadeProcesso(identificador_final, tamanho_processo, self.tamanho_pagina))
        return identificador_final

    def gerar_identificador(self, id_personalizado):
        if id_personalizado and id_personalizado in self.identificadores_em_uso:
            raise Exception("⚠️ Conflito de identificador: O ID especificado já está sendo utilizado. Considere usar um ID automático.")
        elif id_personalizado:
            self.identificadores_em_uso.add(id_personalizado)
            return id_personalizado

        identificador_candidato = self.proximo_id_disponivel
        while identificador_candidato in self.identificadores_em_uso:
            identificador_candidato = self.proximo_id_disponivel
            self.proximo_id_disponivel += 1
        self.identificadores_em_uso.add(identificador_candidato)
        return identificador_candidato

    def obter_processos_ativos(self):
        return self.processos_ativos

    def localizar_processo(self, identificador_processo):
        if identificador_processo is None:
            return None
        for processo in self.processos_ativos:
            if processo.identificador == identificador_processo:
                return processo

    def obter_indice_processo(self, identificador_processo):
        for indice, processo in enumerate(self.processos_ativos):
            if processo.identificador == identificador_processo:
                return indice

    def finalizar_processo(self, processo):
        self.processos_ativos.remove(processo)
        self.processos_finalizados.append(processo) 