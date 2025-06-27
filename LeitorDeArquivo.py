class LeitorDeArquivo:
    def __init__(self, gm):
        self.gm = gm

    def carregar_arquivo(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                linhas = arquivo.readlines()

            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue

                partes = linha.split()  # divide a linha em várias strings diferentes

                id_processo = partes[0]  # P1, P2, P3, etc
                operacao = partes[1]

                if operacao == 'C':
                    tamanho = int(partes[2])

                    if len(partes) > 2:
                        match partes[3]:
                            case 'KB':
                                tamanho *= pow(2, 10)

                            case 'MB':
                                tamanho *= pow(2, 20)

                            case 'GB':
                                tamanho *= pow(2, 30)

                    self.gm.criar_processo(id_processo, tamanho)

                elif operacao == 'R':
                    end_logico = partes[2]
                    resultado = self.gm.leitura_memoria(id_processo, end_logico)
                    if resultado is not None:
                        print(f"Leitura: {resultado}")

                elif operacao == 'W':
                    end_logico = partes[2]
                    conteudo = partes[3]
                    self.gm.escrita_memoria(id_processo, end_logico, conteudo)

                elif operacao == 'P':
                    end_logico = partes[2]
                    self.gm.executar_instrucao_cpu(id_processo, end_logico)

                elif operacao == 'I':
                    dispositivo = partes[2]
                    self.gm.executar_operacao_io(id_processo, dispositivo)

                elif operacao == 'T':
                    self.gm.terminar_processo(id_processo)

        except FileNotFoundError:
            print(f"Arquivo {caminho_arquivo} não encontrado")
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
