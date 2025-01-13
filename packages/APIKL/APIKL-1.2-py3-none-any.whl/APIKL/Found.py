class Found:
    def __init__(self, file_name: str, line: int, key_chance: float, password: str):
        self._file_name = file_name
        self._line = line
        self._key_chance = key_chance
        self._password = password

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = value

    @property
    def line(self) -> int:
        return self._line

    @line.setter
    def line(self, value):
        self._line = value

    @property
    def key_chance(self) -> float:
        return self._key_chance

    @property
    def password(self):
        return self._password

    def get_output_key_chance(self) -> int:
        return round(self._key_chance) if self._key_chance <= 10 else round(self._key_chance, -1)
