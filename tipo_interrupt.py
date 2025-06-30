from enum import Enum

class TipoInterrupt(Enum):
    OP_IO = 0,
    LEITURA_MS = 1
    ESCRITA_MS = 2
