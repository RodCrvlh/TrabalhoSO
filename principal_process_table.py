from typing import List

class PPTEntry:
    def __init__(self, processo_id, pcb_id):
        self.processo_id = processo_id
        self.pcb_id = pcb_id


class PrincipalProcessTable:
    def __int__(self):
        self.processos: List[PPTEntry] = []

    def adicionar_processo(self, processo_id, pcb_id):
        ppt_entry = PPTEntry(processo_id, pcb_id)
        self.processos.append(ppt_entry)

    def get_entrada_ppt(self, processo_id) -> PPTEntry:
        return list(filter(lambda p: p.processo_id == processo_id, self.processos))[0]

    def remover_processo(self, processo_id):
        processo =  self.get_entrada_ppt(processo_id)
        self.processos.remove(processo)

    def update_referencia_pcb(self, processo_id, pcb_id):
        for p in self.processos:
            if p.processo_id == processo_id:
                p.pcb_id = pcb_id
                return
