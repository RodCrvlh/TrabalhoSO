# Sistema de Gerenciamento de Memória Virtual

## 📋 Visão Geral
Este projeto implementa um simulador de sistema de gerenciamento de memória virtual com paginação, incluindo algoritmo LRU (Least Recently Used) para substituição de páginas.

## 🏗️ Arquitetura do Sistema

### Módulos Principais

#### 1. `programa_principal.py`
- **Responsabilidade**: Ponto de entrada do sistema
- **Funções**: Inicialização do sistema e coordenação geral
- **Características**: Interface elegante com usuário e validação de configurações

#### 2. `nucleo_gerenciamento.py`
- **Responsabilidade**: Núcleo central do gerenciamento de memória
- **Funções**: Coordena todas as operações de memória, implementa algoritmo LRU
- **Características**: Gerencia tanto memória principal quanto secundária

#### 3. `entidade_processo.py`
- **Responsabilidade**: Gerenciamento de processos e suas informações
- **Classes**:
  - `EntidadeProcesso`: Representa um processo individual
  - `RegistroProcessos`: Gerencia a tabela de processos ativos
  - `EstadoProcesso`: Enum para estados do processo

#### 4. `subsistema_memoria.py`
- **Responsabilidade**: Gerenciamento direto da memória física e virtual
- **Classes**:
  - `GerenciadorMemoriaPrincipal`: Controla a memória RAM
  - `ArmazenamentoSecundario`: Controla o armazenamento em disco

#### 5. `sistema_paginacao.py`
- **Responsabilidade**: Estruturas de dados para paginação
- **Classes**:
  - `UnidadePagina`: Representa uma página de memória
  - `ElementoMemoria`: Representa um frame de memória
  - `ColecaoPaginasProcesso`: Gerencia páginas de um processo

#### 6. `processador_comandos.py`
- **Responsabilidade**: Interpretação e execução de comandos
- **Funções**: Processa instruções do arquivo de entrada

#### 7. `sistema_logging.py`
- **Responsabilidade**: Sistema de logging e debug
- **Características**: Mensagens elegantes com emojis para melhor visualização

#### 8. `configuracoes.py`
- **Responsabilidade**: Configurações globais do sistema
- **Parâmetros**: Tamanhos de memória, páginas e outros ajustes

## 🚀 Como Executar

```bash
python programa_principal.py
```

## 📝 Formato de Instruções

O sistema processa comandos do arquivo `instrucoes.txt`:

- **C**: Criar processo (ex: `P1 C 512 MB`)
- **R**: Ler memória (ex: `P1 R 10000000000`)
- **W**: Escrever memória (ex: `P1 W 10000000000 1111000`)
- **P**: Executar instrução (ex: `P1 P 0`)
- **T**: Terminar processo (ex: `P1 T`)
- **I**: Operação de E/S (ex: `P1 I 10`)

## ✨ Melhorias Implementadas

### Interface de Usuário
- Mensagens com emojis para melhor experiência visual
- Feedback claro sobre operações do sistema
- Indicadores de progresso para operações demoradas

### Arquitetura
- Consolidação de responsabilidades relacionadas
- Nomes de classes e métodos mais descritivos
- Separação clara entre camadas do sistema

### Logging
- Sistema de debug aprimorado
- Mensagens estruturadas e informativas
- Controle fino sobre níveis de log

## 🎯 Características Técnicas

- **Algoritmo LRU**: Implementação eficiente para substituição de páginas
- **Memória Virtual**: Suporte completo para paginação
- **Validação de Endereços**: Verificação rigorosa de limites de processo
- **Estatísticas**: Monitoramento de uso de memória em tempo real 