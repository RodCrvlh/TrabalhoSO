import threading
from typing import Callable
from tipo_interrupt import TipoInterrupt
import word as w

class DispositivoIO:
    def __init__(self, id):
        self.id = id

    def instrucao_IO(self, process_id, interrupt_handler: Callable[[TipoInterrupt, str, int, list[w.Word] | None], None]):
        print(f"Instrucao IO no dispositivo {self.id} solicitada pelo processo {process_id}")
        threading.Timer(3, self.log_response, args=(TipoInterrupt.OP_IO, process_id, None))


    def log_response(self, process_id, interrupt_handler: Callable[[TipoInterrupt, str, int, list[w.Word] | None], None]):
        print(f"Dispositivo {self.id} finalizando instrução IO para processo {process_id}")
        interrupt_handler(TipoInterrupt.OP_IO, process_id, -1, None)
