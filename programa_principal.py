from sistema_logging import SistemaLogging
from nucleo_gerenciamento import NucleoGerenciamento
from configuracoes import *
from processador_comandos import ProcessadorComandos


def executar_sistema():
    print(f"🏗️ Configuração do Sistema de Memória Virtual")
    print(f"💾 Capacidade da memória principal: {tamanho_memoria_principal} bytes")
    print(f"📄 Tamanho das páginas: {tamanho_pagina} bytes\n")
    
    print("⏳ Inicializando sistema de memória virtual...")
    print("📋 Esta operação pode levar alguns momentos para ser concluída")
    
    if tamanho_memoria_principal % tamanho_pagina != 0:
        raise Exception("⚠️ Erro de configuração: O tamanho da memória não é múltiplo do tamanho da página.")
    
    nucleo_sistema = NucleoGerenciamento(tamanho_memoria_principal, tamanho_pagina)
    processador = ProcessadorComandos(nucleo_sistema)
    processador.executar_arquivo_instrucoes("./instrucoes.txt")
    
    input("\n🎉 Sistema finalizado com sucesso! Pressione qualquer tecla para sair...")

SistemaLogging.ativar_debug()
executar_sistema() 