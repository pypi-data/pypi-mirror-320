from random import randint

from and_tools import Pack, get_random_bin, TEA
from and_tools.Jce_b import JceWriter


def pack_(info, data, types, encryption, sso_seq=None, token=False):
    """组包
    Types:包类型  通常是10 和11
    encryption  加密方式   2 不需要token  1需要token
    sso_seq 包序号
    """
    pack = Pack()
    pack.add_int(types)
    pack.add_bytes(encryption)
    if not info.uin:
        Uin_bytes = bytes.fromhex('30')
    else:
        Uin_bytes = info.uin.encode('utf-8')

    if token:
        D2 = info.UN_Tlv_list.D2_T143
        pack.add_int(len(D2) + 4)
        pack.add_bin(D2)

    if sso_seq is not None:
        pack.add_int(sso_seq)
    pack.add_bytes(0)

    pack.add_int(len(Uin_bytes) + 4)
    pack.add_bin(Uin_bytes)
    pack.add_bin(data)
    bytes_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(bytes_temp) + 4)
    pack.add_bin(bytes_temp)
    return pack.get_bytes()


def pack_head_no_token(info, sBuffer, serviceCmd, sServantName=None, sFuncName=None):
    """照抄的旧源码"""
    # struct com.qq.taf;

    if sServantName is not None:
        """jce部分"""
        iRequestId = randint(110000000, 999999999)
        jce = JceWriter()
        jce.write_int32(3, 1)  # iVersion
        jce.write_int32(0, 2)  # cPacketType
        jce.write_int32(0, 3)  # iMessageType
        jce.write_int64(iRequestId, 4)
        jce.write_string(sServantName, 5)
        jce.write_string(sFuncName, 6)
        jce.write_bytes(sBuffer, 7)
        jce.write_int32(0, 8)  # iTimeout
        _data = jce.bytes()
        _data = _data + bytes.fromhex('98 0C A8 0C')  # 后面的两个空的
    else:
        _data = sBuffer

    pack = Pack()
    pack.add_int(len(serviceCmd) + 4)
    pack.add_bin(bytes(serviceCmd, 'utf-8'))
    pack.add_hex('00 00 00 08')
    pack.add_bin(get_random_bin(4))
    pack.add_hex('00 00 00 04')
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(_data_temp) + 4)
    pack.add_bin(_data_temp)
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_bin(_data_temp)
    pack.add_int(len(_data) + 4)
    pack.add_bin(_data)
    _data = pack.get_bytes()
    _data = TEA.encrypt(_data, info.share_key)

    return _data


def pack_head(info, data, cmd):
    """包头"""
    TokenA4 = info.UN_Tlv_list.TGT_T10A
    if TokenA4 is None:
        TokenA4 = b''

    pack = Pack()
    pack.add_int(info.seq)
    pack.add_int(info.device.app_id)
    pack.add_int(info.device.app_id)

    pack.add_hex('01 00 00 00')
    pack.add_hex('00 00 00 00')
    pack.add_hex('00 00 01 00')
    pack.add_int(len(TokenA4) + 4)
    pack.add_bin(TokenA4)
    pack.add_int(len(cmd) + 4)
    pack.add_bin(bytes(cmd, 'utf-8'))
    pack.add_hex('00 00 00 08')
    pack.add_bin(get_random_bin(4))

    pack.add_body(info.device.Imei, 4, add_len=4)
    pack.add_hex('00 00 00 04')

    pack.add_body(info.device.var, 2, add_len=2)

    bytes_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(bytes_temp) + 4)
    pack.add_bin(bytes_temp)
    bytes_temp = pack.get_bytes()

    pack.empty()
    pack.add_bin(bytes_temp)
    pack.add_int(len(data) + 4)
    pack.add_bin(data)
    bytes_temp = pack.get_bytes()
    bytes_temp = TEA.encrypt(bytes_temp, info.share_key)
    return bytes_temp


def pack_head_login(info, Cmd, Buffer):
    """返回前面的头,后面的单独写在组包的函数里面
    01 8C
    1F 41
    08 12
    """
    pack = Pack()
    pack.add_int(info.seq)
    pack.add_int(info.device.app_id)
    pack.add_int(info.device.app_id)
    pack.add_hex('01 00 00 00 00 00 00 00 00 00 01 00')
    pack.add_body(info.UN_Tlv_list.TGT_T10A, 4, add_len=4)
    pack.add_body(Cmd, 4, add_len=4)
    pack.add_body(get_random_bin(4), length=4, add_len=4)  # MsgCookies
    pack.add_body(info.device.Imei, 4, add_len=4)
    pack.add_hex('00 00 00 04')
    pack.add_body(info.device.var, 2, add_len=2)
    bytes_temp = pack.get_bytes()

    pack.empty()
    pack.add_body(bytes_temp, 4, add_len=4)
    pack.add_body(Buffer, 4, add_len=4)
    data = pack.get_bytes()
    data = TEA.encrypt(data, '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    return data


def PackHead_QMF(info, serviceCmd, Upstream):
    """缝补补,又一年"""
    pack = Pack()
    pack.add_int(len(serviceCmd) + 4)
    pack.add_bin(bytes(serviceCmd, 'utf-8'))
    pack.add_hex('00 00 00 08')
    pack.add_bin(get_random_bin(4))
    pack.add_hex('00 00 00 04')
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_int(len(_data_temp) + 4)
    pack.add_bin(_data_temp)
    _data_temp = pack.get_bytes()

    pack.empty()
    pack.add_bin(_data_temp)
    pack.add_int(len(Upstream) + 4)
    pack.add_bin(Upstream)
    _data = pack.get_bytes()

    Buffer = TEA.encrypt(_data, info.share_key)

    Buffer = pack_(info, Buffer, types=11, encryption=1, sso_seq=info.seq)

    return Buffer
