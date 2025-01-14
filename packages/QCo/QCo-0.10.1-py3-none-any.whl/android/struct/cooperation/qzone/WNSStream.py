# package cooperation.qzone;
import time
import zlib
from typing import Union

from and_tools.Jce_b import JceWriter, JceReader, IJceStruct

from android.struct.QMF_PROTOCAL import QmfUpstream, QmfTokenInfo, QmfClientIpInfo, QmfBusiControl, RetryInfo, \
    QmfDownstream


def createBusiControl(compFlag, length, SUPPORT_COMPRESS):
    Qmf_Busi_Control = QmfBusiControl(
        compFlag=compFlag,
        lenBeforeComp=length,  # 补偿前的长度
        rspCompFlag=SUPPORT_COMPRESS
    ).to_bytes()
    _Buffer = JceWriter().write_jce_struct(Qmf_Busi_Control, 0)

    _Buffer = JceWriter().write_map({'busiCompCtl': {
        'QMF_PROTOCAL.QmfBusiControl': _Buffer
    }}, 0)
    return _Buffer


def createQmfUpstream(info, compFlag: int, BusiBuff: bytes, ServiceCmd: str):
    """"
            创建 Qmf
                compFlag: 比较标志  1 =压缩
                BusiBuff: 业务数据
    """

    Extra = createBusiControl(
        compFlag=compFlag,
        length=len(BusiBuff),  # 压缩前的长度
        SUPPORT_COMPRESS=1

    )

    TokenInfo = QmfTokenInfo(
        Type=64,
        Key=b'',
        ext_key={1: bytearray.fromhex('00')}
    )

    ClientIpInfo = QmfClientIpInfo(
        IpType=0,
        ClientPort=0,
        ClientIpv4=0,
        ClientIpv6=bytearray.fromhex('00 00 00 00 00 00')
    )

    _RetryInfo = RetryInfo(
        Flag=1,
        RetryCount=0,
        PkgId=int(time.time() * 1000)

    )
    if compFlag:
        BusiBuff = zlib.compress(BusiBuff)
    Upstream = QmfUpstream(
        Seq=info.seq,
        Appid=1000027,
        Uin=int(info.uin),
        Qua='V1_AND_SQ_8.9.83_4680_YYB_D',
        ServiceCmd=ServiceCmd,
        DeviceInfo='',
        Token=TokenInfo,
        IpInfo=ClientIpInfo,
        BusiBuff=BusiBuff,
        Extra=Extra,
        flag=0,
        sessionID=0,
        retryinfo=_RetryInfo,

    ).to_bytes()

    return Upstream


def UnQmfDownstream(Buffer: bytes, key_1: str, key_2: str):
    """解QMF"""

    stream = QmfDownstream()
    stream.read_from(JceReader(Buffer))

    Buffer_head = stream.BusiBuff[:1]
    if Buffer_head == bytearray(b'x'):
        BusiBuff = zlib.decompress(stream.BusiBuff)
    else:
        BusiBuff = stream.BusiBuff

    BusiBuff = JceReader(BusiBuff).read_map(0)

    rsp_Buffer = BusiBuff.get(key_1, {}).get(key_2, b'')
    msg_Buffer = BusiBuff.get('msg', {}).get('string', b'')
    ret_Buffer = BusiBuff.get('ret', {}).get('int32', b'')
    msg = JceReader(msg_Buffer).read_string(0)
    ret = JceReader(ret_Buffer).read_int64(0)

    return rsp_Buffer, msg, ret
