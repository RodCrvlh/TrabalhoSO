from typing import List

class PPTEntry:
    pcb_address: int

    def __init__(self, id_processo):
        self.id_processo = id_processo


class PrincipalProcessTable:
    def __int__(self):
        self.processos: List[PPTEntry] = []


    def adicionar_processo(self, id_processo):
        ppt_entry = PPTEntry(id_processo)
        self.processos.append(ppt_entry)


    def processo_existe(self, id_processo):
        return any(p.id_processo == id_processo for p in self.processos)


    def get_entrada_ppt(self, id_processo) -> PPTEntry:
        return list(filter(lambda p: p.id_processo == id_processo, self.processos))[0]


    def remover_processo(self, id_processo):
        processo =  self.get_entrada_ppt(id_processo)
        self.processos.remove(processo)


    def update_referencia_pcb(self, id_processo, pcb_end):
        for p in self.processos:
            if p.id_processo == id_processo:
                p.pcb_address = pcb_end
                return
