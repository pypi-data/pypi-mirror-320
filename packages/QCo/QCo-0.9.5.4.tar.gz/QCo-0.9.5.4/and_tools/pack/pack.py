from and_tools.byte_ import hex_format


class Pack:
    """组包
    好像作用不大....
    """

    def __init__(self):
        self._bytes_data = bytearray()

    def add_bin(self, bytes_temp):
        if bytes_temp is not None:
            self._bytes_data.extend(bytes_temp)

    def add_hex(self, bytes_temp):
        if bytes_temp is not None:
            self._bytes_data.extend(bytearray.fromhex(bytes_temp))

    def add_bytes(self, bytes_temp):
        """字节或字节集"""
        if bytes_temp is not None:
            self._bytes_data.append(bytes_temp)

    def add_int(self, int_temp, length=4):
        """整数
        length:
        int:4
        Short:2
        long:8
        """
        if int_temp is not None:
            self._bytes_data.extend(int_temp.to_bytes(length, 'big'))

    def add_body(self, data, length=4, _hex=False, add_len=0):
        """头部&内容"""
        if data is None:
            return

        if isinstance(data, str):
            bytes_data = bytes.fromhex(data) if _hex else data.encode('utf-8')
        else:
            bytes_data = data

        self.add_int(len(bytes_data) + add_len, length)
        self.add_bin(bytes_data)

    def set_data(self, byte_temp):
        """置数据"""
        if byte_temp is not None:
            self._bytes_data = byte_temp

    def empty(self):
        """清空"""
        self._bytes_data = bytearray()

    def get_bytes(self, _hex=False):
        if _hex:
            _bytes_temp = self._bytes_data.hex()
            _bytes_temp = hex_format(_bytes_temp)
        else:
            _bytes_temp = self._bytes_data
        return _bytes_temp
