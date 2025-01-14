class UnPack:
    """解包"""

    def __init__(self, data):
        if isinstance(data, str):
            self._byte_data = bytearray.fromhex(data.replace(' ', ''))
        else:
            self._byte_data = data

    def _get_bytes(self, length: int) -> bytes:
        res = self._byte_data[:length]
        self._byte_data = self._byte_data[length:]
        return res

    def get_int(self, length=4):
        """取整数"""
        res = self._get_bytes(length)
        return int.from_bytes(res, 'big')

    def get_long(self):
        """取长整数"""
        res = self._get_bytes(8)
        return int.from_bytes(res, 'big')

    def get_byte(self):
        """取字节"""
        res = self._get_bytes(1)
        return int.from_bytes(res, 'big', signed=True)

    def get_bin(self, length):
        """取字节集"""
        res = self._get_bytes(length)
        return res

    def get_short(self):
        """取短整数"""
        res = self._get_bytes(2)
        return int.from_bytes(res, 'big')

    def get_len(self):
        """取长度"""
        return len(self._byte_data)

    def get_all(self, _hex=False):
        """取全部"""
        res = self._byte_data[:]
        if _hex:
            res = ' '.join(['{:02x}'.format(byte) for byte in res])
        return res
