from random import randint
from enum import Enum

class Instrucao(Enum):
    SOMA = 0,
    SUB = 1

class TipoWord(Enum):
    DADO = 0,
    INSTRUCAO = 1

class Word:
    dado: int
    instrucao: Instrucao

    def __init__(self, tipo: TipoWord = TipoWord.DADO):
        self.tipo : TipoWord = tipo # Dado | Instrucao

    def set_dado(self, dado: int):
        self.dado = dado

    def set_instrucao(self, instrucao: Instrucao):
        self.instrucao = instrucao

    def fill_with_trash(self):
        self.dado = randint(-2147483648, 2147483647)
        return self
