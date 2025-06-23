# Estrutura que mantem os dados e quadros armazenados
class MemoriaPrincipal:
    # inicializa uma entrada da MemoriaFisica
    def __init__(self, n_quadros, tam_quadro):
        self.n_quadros = n_quadros
        self.tam_quadro = tam_quadro
        self.quadros = self.init_quadros()

    def init_quadros(self):
        quadros = []
        for _ in range(self.n_quadros):
            quadro = {
                'Conteudo': [""] * self.tam_quadro,
                'Processo': -1,
                'Pagina': -1
            }
            quadros.append(quadro)
        return quadros

    def esta_cheio(self):
        for i in range(self.n_quadros):
            if self.quadros[i]['Processo'] == -1:
                return False

        return True

    def ler(self, n_quadro):
        return self.quadros[n_quadro]

    def escrever(self, n_quadro, offset, conteudo):
        if n_quadro >= self.n_quadros:
            print("Endereço invalido")
            return None

        self.quadros[n_quadro]['Conteudo'][offset] = conteudo

    def alocar_quadro(self, processo, pagina, conteudo):
        for i, quadro in enumerate(self.quadros):
            if quadro['Pagina'] == -1:
                quadro['Pagina'] = pagina
                quadro['Processo'] = processo
                quadro['Conteudo'] = conteudo
                print(i)
                return i
        return -1

    def liberar_quadro(self, id_quadro):
        if id_quadro >= self.n_quadros:
            print("Quadro inexistente")
            return

        self.quadros[id_quadro] = {
            'Conteudo': [""] * self.tam_quadro,
            'Processo': -1,
            'Pagina': -1
        }

    def mostrar(self):
        print("Memoria Principal:")
        print("------------------------------------")
        for i, quadro in enumerate(self.quadros):
            if quadro['Processo'] == -1:
                print(f"Quadro {i}: Livre")
            else:
                print(f"Quadro {i}: Processo{quadro['Processo']}, Pagina:{quadro['Pagina']}, "
                      f"Conteudo:{quadro['Conteudo']}")
        print("------------------------------------")
