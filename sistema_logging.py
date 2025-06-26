class SistemaLogging:
    debug_ativo = False

    @classmethod
    def registrar(cls, mensagem):
        if not cls.debug_ativo:
            return
        print(f"🔍 {mensagem}")

    @classmethod
    def ativar_debug(cls):
        cls.debug_ativo = True

    @classmethod
    def desativar_debug(cls):
        cls.debug_ativo = False 