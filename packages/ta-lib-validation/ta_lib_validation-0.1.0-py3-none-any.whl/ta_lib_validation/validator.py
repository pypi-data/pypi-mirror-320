class InputValidator:
    @staticmethod
    def validateInt(val: object) -> bool:
        return isinstance(val, int)

    @staticmethod
    def validateIntStr(val: object) -> bool:
        if isinstance(val, int):
            return True
        
        if isinstance(val, str):
            try:
                _ = int(val)
                return True
            except ValueError:
                return False