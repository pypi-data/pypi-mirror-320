from typing import Union

from and_tools.Jce_b import IJceStruct
from and_tools.Jce_b.typing import JceReader


class s_user(IJceStruct):
    def read_from(self, reader: JceReader) -> None:
        pass

    def to_bytes(self) -> Union[bytes, bytearray]:
        pass
