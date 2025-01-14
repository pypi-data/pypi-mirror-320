import datetime
import time

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


def wtlogin_trans(bArr):
    """k值 变体解法"""
    a_sm = b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff>\xff\xff?\xff\xff456789:;<=\xff\xff\xff' \
           b'\xff\xff\xff\xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16' \
           b'\x17\x18\x19\xff\xff\xff\xff\xff\xff\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,' \
           b'-./0123\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
           b'\xff\xff\xff\xff\xff'
    if isinstance(bArr, str):
        bArr = bArr.encode()

    i = 32
    i4 = 0
    i3 = 0
    i2 = 0
    b = 0
    bArr2 = bytearray(24)
    while True:
        i6 = i - 1
        if i > 0:
            i7 = i4 + 1
            i5 = bArr[i4]

            if i5 != 0 or i5 == 95:
                if i5 == 32:
                    i5 = 42

                b2 = a_sm[i5]
                if b2 < 0:
                    b = b2
                    i = i6
                    i4 = i7
                else:
                    residue = i3 % 4
                    if residue == 0:
                        bArr2[i2] = b2 << 2
                        i5 = i2
                    elif residue == 1:
                        i5 = i2 + 1

                        bArr2[i2] = bArr2[i2] | (b2 >> 4)
                        bArr2[i5] = (b2 & 0x0F) << 4

                    elif residue == 2:
                        i5 = i2 + 1
                        bArr2[i2] = bArr2[i2] | (b2 >> 2)
                        bArr2[i5] = (b2 & 0x03) << 6
                    elif residue == 3:
                        i5 = i2 + 1
                        bArr2[i2] |= b2
                    else:
                        i5 = i2

                i3 += 1
                i4 = i7
                i = i6
                i2 = i5
                b = b2


        elif b == 95:
            residue = i3 / 4
            if residue == 1:
                break
            elif residue == 2:
                i2 = i2 + 1
        else:
            break

    return bArr2


def trans_emp_auth(info, **kwargs):
    verify = kwargs.get('verify', False)
    pack = Pack()
    pack.add_int(int(time.time()))

    if verify:
        pack.add_hex(
            '02 00 C9 00 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 32 00 00 00 02 00 00 00 00')
    else:
        pack.add_hex(
            '02 00 DE 00 13 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 32 00 00 00 00 00 00 00 00')

    pack.add_int(int(info.uin))
    pack.add_hex('00 00 00 00 00 10 00 00 00 00')
    pack.add_int(int(info.uin))
    pack.add_body(wtlogin_trans(kwargs['K']), 2)
    pack.add_body(info.UN_Tlv_list.TGT_T10A, 2)
    if verify:
        pack.add_hex('08 00 03 00 02 00 08 00 00 00 00 00 00 00 0B 00 15 00 04 00 00 00 00 00 68')
        pack.add_body(info.Guid, 2)
    else:
        pack.add_bin(info.Guid)
        pack.add_hex('01 00 01 08 00 04 00 03 00 05 00 20 00 36 00 01 00 09')
        pack.add_body('com.tencent.mobileqq', 2)  # 似乎会对其识别
        pack.add_hex('00 39 00 04 00 00 00 01')

    pack.add_hex('03')
    data = TEA.encrypt(pack.get_bytes(), info.UN_Tlv_list.userSt_Key)

    pack.empty()
    if verify:
        pack.add_hex('01 00 D8 00 00 00 10 00 00 00 72 00 60')
    else:
        pack.add_hex('01 00 F0 00 00 00 10 00 00 00 72 00 60')
    pack.add_bin(info.UN_Tlv_list.userStSig)
    pack.add_hex('00')
    pack.add_bin(data)

    data = TEA.encrypt(pack.get_bytes(), info.UN_Tlv_list.wtSessionTicketKey)

    pack.empty()
    pack.add_hex('1F 41')
    pack.add_hex('08 12')
    pack.add_hex('00 01')
    pack.add_int(int(info.uin))  # Uin_bytes
    pack.add_hex('03 45 00 00 00 00 02 00 00 00 00 00 00 00 00 00 30')
    pack.add_bin(info.UN_Tlv_list.wtSessionTicket)
    pack.add_bin(data)

    data = pack.get_bytes()

    pack.empty()  # 包裹
    pack.add_hex('02')
    pack.add_int(len(data) + 4, 2)  # 短整数
    pack.add_bin(data)
    pack.add_hex('03')

    data = pack.get_bytes()

    pack.empty()
    pack.add_hex(
        '00 00 00 27 00 00 00 15 77 74 6C 6F 67 69 6E 2E 74 72 61 6E 73 5F 65 6D 70 00 00 00 08 F7 C0 A1 E8 00 00 00 06 70 00')
    pack.add_int(len(data) + 4, 4)
    pack.add_bin(data)
    data = TEA.encrypt(pack.get_bytes(), '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
    # 头部
    data = pack_(info, data=data, encryption=2, types=11, sso_seq=info.seq)
    return data


def trans_emp_auth_res(data, info, **kwargs):
    auth_info = {}
    verify = kwargs.get('verify', False)
    auth_info['verify'] = verify
    data = TEA.decrypt(data[16:-1], info.UN_Tlv_list.wtSessionTicketKey)
    data = TEA.decrypt(data[5:], info.UN_Tlv_list.userSt_Key)
    data = data[53:]
    pack = UnPack(data)
    status = pack.get_byte()

    if status != 0:
        _len = pack.get_short()
        message = pack.get_bin(_len).decode('utf-8')
        auth_info['message'] = message
    else:
        _time = pack.get_int(4)
        _len = pack.get_short()
        AuthName = pack.get_bin(_len).decode('utf-8')
        auth_info['AuthName'] = AuthName
        if verify:
            # 确认授权
            pack.get_short()
        data = pack.get_all()
        TLv = UnTlv(data, info)
        TLv.unpack()

        auth_info.update(TLv.get_auth_result())
    auth_info['status'] = status
    return auth_info
