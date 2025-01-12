import datetime

from and_tools import Pack, TEA, UnPack, get_md5
from android.utils import pack_
from android.utils.head import pack_head_login
from android.wlogin_sdk.tlv import TLV
from android.wlogin_sdk.tlv_res import UnTlv


def wtlogin_exchange_emp(info):
    """"
    更新令牌,todo 需要修改公钥和私钥
    :param info:
    """

    info.key_Pubkey = bytes.fromhex(
        '04 70 83 E0 93 38 B0 49 98 89 88 B7 8B 87 D8 B0 03 CE 45 B2 6D A6 92 21 84 67 A0 63 49 6F 78 B3 36 06 36 E2 19 8D 18 85 57 DA 0D 30 2D 2E 53 1E 2C C2 2C 21 4B 92 7F 8A 5B BC CC AD 33 19 AF F3 1A')
    _tlv = TLV(info)

    methods = [
        _tlv.T100(5, 16, 0, 34869472),
        _tlv.T10A(info.UN_Tlv_list.TGT_T10A),

        _tlv.T116(2),
        _tlv.T143(info.UN_Tlv_list.D2_T143),

        _tlv.T142(),
        _tlv.T154(),

        _tlv.T017(info.device.app_id, int(info.uin), info.login_time),
        _tlv.T141(),

        _tlv.T008(),

        _tlv.T147(),

        _tlv.T177(),
        _tlv.T187(),
        _tlv.T188(),
        _tlv.T202(),
        _tlv.T511()
    ]

    pack = Pack()
    pack.add_hex('00 0B')
    pack.add_int(len(methods), 2)  # 数量
    for method_result in methods:
        pack.add_bin(method_result)

    Buffer_tlv = pack.get_bytes()

    Buffer_tlv = TEA.encrypt(Buffer_tlv, bytes.fromhex('48 23 99 47 A6 E9 76 DF A5 43 26 F1 FB DE 51 18'))

    pack.empty()
    pack.add_hex('1F 41')
    pack.add_hex('08 10')
    pack.add_hex('00 01')
    pack.add_int(int(info.uin))
    pack.add_hex('03 07 00 00 00 00 02 00 00 00 00 00 00 00 00')
    pack.add_hex('02 01')

    pack.add_bin(info.key_rand)
    pack.add_hex('01 31')
    pack.add_hex('00 01')
    pack.add_body(info.key_Pubkey, 2)
    pack.add_bin(Buffer_tlv)
    Buffer = pack.get_bytes()

    pack.empty()
    pack.add_hex('02')
    pack.add_body(Buffer, 2, add_len=4)
    pack.add_hex('03')
    Buffer = pack.get_bytes()
    pack.empty()
    Buffer = pack_head_login(info, 'wtlogin.exchange_emp', Buffer)
    Buffer = pack_(info, data=Buffer, encryption=2, types=10, sso_seq=4)
    return Buffer


def wtlogin_exchange_emp_rsp(info, Buffer: bytes):
    # 其实和登录返回没区别
    Buffer = Buffer[15:-1]  # 头部 15字节&去掉尾部03
    _status = Buffer[0]

    Buffer = TEA.decrypt(Buffer[1:], bytes.fromhex('48 23 99 47 A6 E9 76 DF A5 43 26 F1 FB DE 51 18'))
    if _status == 0:
        Buffer = Buffer[5:]  # 00 09 00 00 02

        pack = UnPack(Buffer)
        _head = pack.get_bin(2).hex()
        _len = pack.get_short()
        Buffer = pack.get_bin(_len)

        if _head == '0119':
            # 判断tlv的头部
            Buffer = TEA.decrypt(Buffer, get_md5(info.share_key))

    else:
        Buffer = Buffer[3:]
    un_tlv = UnTlv(Buffer, info)
    un_tlv.unpack()
    if _status == 0:
        info.emp_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {'status': _status, 'cookie': info.cookies}

    return {'status': _status, 'message': '缓存更新异常'}
