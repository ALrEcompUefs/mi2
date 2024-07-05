from abc import ABC
from typing import NamedTuple


class ComentarioBlocoAberto(ABC, Exception):
    pass

class Token(NamedTuple):
    line : int
    code : str
    token : str

class TokenDefeituoso(NamedTuple):
    line : int
    code : str
    token : str

class SintaxeMalFormada(NamedTuple):
    start_line: int
    end_line: int
    read_token: str
    expected_token: list
