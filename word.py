from random import randint
from enum import Enum

class Instrucao(Enum):
    SOMA = 0,
    SUB = 1

class TipoWord(Enum):
    DADO = 0,
    INSTRUCAO = 1

class Word:
    tipo: TipoWord
    dado: int
    instrucao: Instrucao

    def __init__(self, tipo: TipoWord = TipoWord.DADO):
        self.tipo = tipo # Dado | Instrucao | None

    def set_dado(self, dado: int):
        self.dado = dado

    def set_instrucao(self, instrucao: Instrucao):
        self.instrucao = instrucao

    def fill_with_trash(self):
        self.tipo = TipoWord.DADO
        self.dado = randint(-2147483648, 2147483647)
        return self


def copy_word(word: Word | None = None) -> Word:
    if not word:
        return Word().fill_with_trash()

    copied_word = Word(word.tipo)
    if word.tipo == TipoWord.DADO:
        copied_word.set_dado(word.dado)
    else:
        copied_word.set_instrucao(word.instrucao)
    return copied_word
