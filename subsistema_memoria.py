from typing import List
from math import ceil
from sistema_logging import SistemaLogging
from sistema_paginacao import UnidadePagina, ElementoMemoria


class GerenciadorMemoriaPrincipal:
    def __init__(self, tamanho_total_memoria, tamanho_frame):
        self.proximo_indice_disponivel = 0
        self.estrutura_frames: List[ElementoMemoria] = []
        self._inicializar_frames(tamanho_total_memoria, tamanho_frame)

    def _inicializar_frames(self, tamanho_total_memoria, tamanho_frame):
        quantidade_frames = tamanho_total_memoria // tamanho_frame
        SistemaLogging.registrar(
            f"🏗️ Estruturando memória: {tamanho_total_memoria} bytes divididos em {quantidade_frames} frames de {tamanho_frame} bytes cada.")
        for indice in range(quantidade_frames):
            self.estrutura_frames.append(ElementoMemoria(tamanho_frame))

    def alocar_espaco(self, pagina: UnidadePagina, ciclo_atual):
        indice_frame, frame_candidato = self.obter_proximo_frame()
        ponto_inicial_busca = indice_frame

        if not frame_candidato.ocupado:
            SistemaLogging.registrar(f"✅ Frame {indice_frame} disponível. Realizando alocação")
            frame_candidato.ocupado = True
            pagina.numero_frame = indice_frame
            pagina.timestamp_ultimo_acesso = ciclo_atual
            pagina.presente_memoria_principal = True
            return True
        SistemaLogging.registrar(f"❌ Frame {indice_frame} não disponível.")

        while indice_frame != ponto_inicial_busca:
            indice_frame, frame_candidato = self.obter_proximo_frame()
            if not frame_candidato.ocupado:
                SistemaLogging.registrar(f"✅ Frame {indice_frame} disponível. Realizando alocação")
                frame_candidato.ocupado = True
                pagina.numero_frame = indice_frame
                pagina.timestamp_ultimo_acesso = ciclo_atual
                pagina.presente_memoria_principal = True
                return True
            SistemaLogging.registrar(f"❌ Frame {indice_frame} não disponível.")
        SistemaLogging.registrar("⚠️ Nenhum frame disponível encontrado na memória principal.")
        return False

    def liberar_frames(self, pagina: UnidadePagina):
        frame_alvo = self.estrutura_frames[pagina.numero_frame]
        frame_alvo.ocupado = False
        for posicao in range(len(frame_alvo.dados)):
            frame_alvo.dados[posicao] = 0
        return

    def obter_proximo_frame(self):
        frame_atual = self.estrutura_frames[self.proximo_indice_disponivel]
        indice_atual = self.proximo_indice_disponivel
        self.proximo_indice_disponivel = (self.proximo_indice_disponivel + 1) % len(self.estrutura_frames)
        return indice_atual, frame_atual

    def verificar_disponibilidade(self, quantidade_paginas_necessarias):
        contador_livres = 0
        for frame in self.estrutura_frames:
            if not frame.ocupado:
                contador_livres += 1
                if contador_livres == quantidade_paginas_necessarias:
                    return True
        return False

    def contar_frames_ocupados(self):
        contador = 0
        for frame in self.estrutura_frames:
            if frame.ocupado:
                contador += 1
        return contador

    def obter_total_frames(self):
        return len(self.estrutura_frames)


class ArmazenamentoSecundario:
    def __init__(self, tamanho_total_armazenamento, tamanho_pagina):
        self.capacidade_total_frames = ceil(tamanho_total_armazenamento / tamanho_pagina)
        self.repositorio_virtual = []

    def armazenar_pagina(self, pagina: UnidadePagina, frame: ElementoMemoria):
        if len(self.repositorio_virtual) >= self.capacidade_total_frames:
            print("⚠️ Capacidade máxima do armazenamento secundário atingida!")
            return

        self.repositorio_virtual.append(_UnidadeArmazenamentoVirtual(frame, pagina))
        print(f"💾 Página {pagina.identificador_pagina} do processo P{pagina.identificador_processo} foi transferida para o armazenamento secundário")

    def recuperar_pagina(self, pagina_solicitada):
        for indice in range(len(self.repositorio_virtual)):
            pagina_armazenada = self.repositorio_virtual[indice].pagina_referencia
            if (pagina_armazenada.identificador_pagina == pagina_solicitada.identificador_pagina and 
                pagina_armazenada.identificador_processo == pagina_solicitada.identificador_processo):
                unidade_recuperada = self.repositorio_virtual.pop(indice)
                return unidade_recuperada.dados_preservados
        print(f"🔍 Página {pagina_solicitada.identificador_pagina} do processo P{pagina_solicitada.identificador_processo} não localizada no armazenamento secundário")
        return None

    def contar_frames_utilizados(self):
        return len(self.repositorio_virtual)


class _UnidadeArmazenamentoVirtual:
    def __init__(self, frame: ElementoMemoria, pagina: UnidadePagina):
        self.dados_preservados = self._preservar_conteudo_frame(frame)
        self.pagina_referencia = pagina

    def _preservar_conteudo_frame(self, frame):
        dados_preservados = []
        if frame is not None:
            for posicao in range(frame.tamanho):
                if frame.dados[posicao] != 0:
                    dados_preservados.append((posicao, frame.dados[posicao]))
        return dados_preservados 