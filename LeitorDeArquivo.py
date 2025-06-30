class LeitorDeArquivo:
    def carregar_arquivo(self, caminho_arquivo) -> list[str]:
        try:
            with open(caminho_arquivo, 'r') as arquivo:
                linhas = arquivo.readlines()

            programa = []
            for linha in linhas:
                programa.append(linha.strip())
                if not linha:
                    continue

            return programa

        except FileNotFoundError:
            print(f"Arquivo {caminho_arquivo} não encontrado")
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
        return []
