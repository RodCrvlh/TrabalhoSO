from math import ceil
from typing import List
from random import randint

from entidade_processo import EntidadeProcesso
from sistema_logging import SistemaLogging
from subsistema_memoria import GerenciadorMemoriaPrincipal, ArmazenamentoSecundario
from sistema_paginacao import UnidadePagina
from entidade_processo import RegistroProcessos
from configuracoes import *


class NucleoGerenciamento:

    def __init__(self, tamanho_memoria_principal, tamanho_pagina):
        self.tamanho_pagina = tamanho_pagina
        self.tamanho_memoria_principal = tamanho_memoria_principal
        SistemaLogging.registrar("🚀 Inicializando sistema de registro de processos")
        self.registro_processos = RegistroProcessos(tamanho_pagina)
        SistemaLogging.registrar("🏗️ Configurando subsistema de memória principal")
        self.memoria_principal = GerenciadorMemoriaPrincipal(tamanho_memoria_principal, tamanho_pagina)
        SistemaLogging.registrar("✅ Subsistema de memória principal configurado com sucesso\n")
        self.armazenamento_secundario = ArmazenamentoSecundario(tamanho_memoria_secundaria, tamanho_pagina)
        SistemaLogging.registrar("✅ Subsistema de armazenamento secundário configurado com sucesso\n")

    def verificar_espaco_disponivel(self, tamanho_solicitado: int):
        espaco_livre_principal = self.calcular_espaco_livre_principal()
        espaco_livre_secundario = (self.armazenamento_secundario.capacidade_total_frames -
                              self.armazenamento_secundario.contar_frames_utilizados()) * tamanho_pagina
        return (espaco_livre_secundario + espaco_livre_principal) >= tamanho_solicitado

    def criar_processo(self, tamanho_solicitado, ciclo_atual, id_processo=None):
        SistemaLogging.registrar(f"🔄 Iniciando criação de processo com {tamanho_solicitado} bytes")
        espaco_suficiente = self.verificar_espaco_disponivel(tamanho_solicitado)
        if espaco_suficiente:
            SistemaLogging.registrar(f"✅ Recursos suficientes identificados no sistema de memória\n")
            id_final = self.registro_processos.criar_novo_processo(tamanho_solicitado, id_processo)
            SistemaLogging.registrar(
                f"📋 Processo P{id_final} registrado no índice {self.registro_processos.obter_indice_processo(id_final)}\n")
            processo = self.registro_processos.localizar_processo(id_final)
            SistemaLogging.registrar(f"🔍 Verificando disponibilidade de {tamanho_solicitado} bytes na memória principal")
            SistemaLogging.registrar(f"📦 Alocando páginas no sistema de memória")
            self.alocar_paginas_do_processo(processo.obter_paginas(), ciclo_atual)
            SistemaLogging.registrar(
                f"🎉 Processo alocado com êxito no sistema\n"
                f"📊 Utilização da memória principal: {self.calcular_percentual_uso_principal() * 100:.2f}%\n"
                f"📊 Utilização do armazenamento secundário: {self.calcular_percentual_uso_secundario() * 100:.2f}%\n")
            return
        SistemaLogging.registrar(f"❌ Espaço insuficiente no sistema. Alocação cancelada")

    def calcular_percentual_uso_secundario(self):
        return self.armazenamento_secundario.contar_frames_utilizados() / self.armazenamento_secundario.capacidade_total_frames
    
    def calcular_percentual_uso_principal(self):
        return self.memoria_principal.contar_frames_ocupados() / self.memoria_principal.obter_total_frames()

    def calcular_quantidade_paginas(self, tamanho):
        return ceil(tamanho / self.tamanho_pagina)

    def alocar_paginas_do_processo(self, conjunto_paginas: List[UnidadePagina], ciclo_atual):
        for indice, pagina in enumerate(conjunto_paginas):
            if not pagina.presente_memoria_principal:
                SistemaLogging.registrar(f"📄 Página {indice} ausente da memória principal.")
                if self.memoria_principal.contar_frames_ocupados() < self.memoria_principal.obter_total_frames():
                    self.memoria_principal.alocar_espaco(pagina, ciclo_atual)
                else:
                    self.armazenamento_secundario.armazenar_pagina(pagina, None)
                SistemaLogging.registrar(f"✅ Página {indice} alocada com sucesso\n")
            else:
                SistemaLogging.registrar(f"✅ Página {indice} já presente na memória principal. Prosseguindo")

    def calcular_espaco_livre_principal(self):
        return (self.memoria_principal.obter_total_frames() - self.memoria_principal.contar_frames_ocupados()) * tamanho_pagina

    def calcular_uso_bytes_secundario(self):
        return self.armazenamento_secundario.contar_frames_utilizados() * tamanho_pagina

    def executar_leitura_memoria(self, id_processo, endereco_logico, ciclo_atual):
        processo = self.registro_processos.localizar_processo(id_processo)

        informacoes_pagina = processo.calcular_pagina_e_offset(endereco_logico)

        print(f"📖 Executando leitura na página {informacoes_pagina['pagina']}, offset {informacoes_pagina['offset']} do processo P{id_processo}")
        pagina_solicitada = processo.obter_paginas()[informacoes_pagina['pagina']]
        if not pagina_solicitada.presente_memoria_principal:
            self.aplicar_algoritmo_lru(pagina_solicitada, ciclo_atual)
        frame_alvo = self.memoria_principal.estrutura_frames[pagina_solicitada.numero_frame]
        print(
            f"📊 Valor encontrado no offset {informacoes_pagina['offset']} do frame {pagina_solicitada.numero_frame}: {frame_alvo.dados[informacoes_pagina['offset']]}")
        pagina_solicitada.timestamp_ultimo_acesso = ciclo_atual
        return

    def executar_escrita_memoria(self, id_processo, endereco_logico, valor, ciclo_atual):
        processo = self.registro_processos.localizar_processo(id_processo)

        informacoes_pagina = processo.calcular_pagina_e_offset(endereco_logico)

        print(f"✏️ Executando escrita na página {informacoes_pagina['pagina']}, offset {informacoes_pagina['offset']} do processo P{id_processo}")
        pagina_solicitada = processo.obter_paginas()[informacoes_pagina['pagina']]
        if not pagina_solicitada.presente_memoria_principal:
            self.aplicar_algoritmo_lru(pagina_solicitada, ciclo_atual)
        frame_alvo = self.memoria_principal.estrutura_frames[pagina_solicitada.numero_frame]
        frame_alvo.dados[informacoes_pagina["offset"]] = valor
        pagina_solicitada.modificada = True
        print(f"💾 Valor {valor} gravado no offset {informacoes_pagina['offset']} do frame {pagina_solicitada.numero_frame}")
        pagina_solicitada.timestamp_ultimo_acesso = ciclo_atual
        return

    def executar_instrucao(self, id_processo, endereco_logico, ciclo_atual):
        processo = self.registro_processos.localizar_processo(id_processo)

        informacoes_pagina = processo.calcular_pagina_e_offset(endereco_logico)

        print(
            f"⚡ Executando instrução na página {informacoes_pagina['pagina']}, offset {informacoes_pagina['offset']} do processo P{id_processo}")
        pagina_solicitada = processo.obter_paginas()[informacoes_pagina['pagina']]
        if not pagina_solicitada.presente_memoria_principal:
            self.aplicar_algoritmo_lru(pagina_solicitada, ciclo_atual)
        resultado_computacao = randint(0, 10000)
        tipo_operacao = "adição" if endereco_logico % 2 == 0 else "subtração"
        print(
            f"🧮 Resultado da {tipo_operacao} na página {informacoes_pagina['pagina']}, offset {informacoes_pagina['offset']} do processo P{id_processo}: {resultado_computacao}")
        pagina_solicitada.timestamp_ultimo_acesso = ciclo_atual
        return

    def acessar_dispositivo_io(self, id_processo, identificador_dispositivo):
        print(f"🔌 Processo P{id_processo} está realizando operação de E/S no dispositivo {identificador_dispositivo}")

    def aplicar_algoritmo_lru(self, pagina_solicitada: UnidadePagina, ciclo_atual):
        pagina_menos_recente = self.registro_processos.obter_processos_ativos()[0].obter_paginas()[0]
        for processo in self.registro_processos.obter_processos_ativos():
            for pagina in processo.obter_paginas():
                if not pagina_menos_recente.presente_memoria_principal:
                    pagina_menos_recente = pagina
                elif pagina.presente_memoria_principal and pagina.timestamp_ultimo_acesso < pagina_menos_recente.timestamp_ultimo_acesso:
                    pagina_menos_recente = pagina
        print(
            f"🔄 Aplicando algoritmo LRU: Substituindo página do frame {pagina_menos_recente.numero_frame} (P{pagina_menos_recente.identificador_processo}) por página {pagina_solicitada.identificador_pagina} (P{pagina_solicitada.identificador_processo})")

        pagina_menos_recente.presente_memoria_principal = False
        self.armazenamento_secundario.armazenar_pagina(pagina_menos_recente,
                                             self.memoria_principal.estrutura_frames[pagina_menos_recente.numero_frame])
        self.memoria_principal.liberar_frames(pagina_menos_recente)
        pagina_menos_recente.numero_frame = None
        pagina_menos_recente.timestamp_ultimo_acesso = None
        
        conteudo_recuperado = self.armazenamento_secundario.recuperar_pagina(pagina_solicitada)
        self.memoria_principal.alocar_espaco(pagina_solicitada, ciclo_atual)

        if conteudo_recuperado is not None and len(conteudo_recuperado) > 0:
            frame_destino = self.memoria_principal.estrutura_frames[pagina_solicitada.numero_frame]
            while len(conteudo_recuperado) > 0:
                item = conteudo_recuperado.pop()
                frame_destino.dados[item[0]] = item[1]
        return

    def finalizar_processo(self, id_processo, ciclo_atual):
        print(f"🔚 Iniciando finalização do processo P{id_processo}\n⏳ Esta operação pode demorar alguns momentos...")
        processo = self.registro_processos.localizar_processo(id_processo)
        for i in range(len(processo.obter_paginas())):
            pagina = processo.obter_paginas()[0]
            self.desalocar_pagina(pagina, processo)
        processo.finalizar_processo()
        self.registro_processos.finalizar_processo(processo)

    def desalocar_pagina(self, pagina: UnidadePagina, processo: EntidadeProcesso):
        if pagina.presente_memoria_principal:
            self.memoria_principal.liberar_frames(pagina)
        else:
            self.armazenamento_secundario.recuperar_pagina(pagina)
        processo.gerenciador_paginas.remover_pagina(pagina) 