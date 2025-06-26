class LoggingSystem:
    debug_active = False

    @classmethod
    def log(cls, message):
        if not cls.debug_active:
            return
        print(f"🔍 {message}")

    @classmethod
    def enable_debug(cls):
        cls.debug_active = True

    @classmethod
    def disable_debug(cls):
        cls.debug_active = False 