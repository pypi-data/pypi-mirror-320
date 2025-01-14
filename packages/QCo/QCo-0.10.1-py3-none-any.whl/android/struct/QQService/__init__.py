import zlib

from and_tools.Jce import JceInputStream, JceStruct
from and_tools.Jce_b import JceWriter
from .SvcReqGetDevLoginInfo import SvcReqGetDevLoginInfo
from ...utils import pack_head_no_token, pack_, un_jce_head, un_jce_head_2


def GetDevLoginInfo_profile(info, item: SvcReqGetDevLoginInfo):
    """获取设备登录信息"""
    _buffer = item.to_bytes()
    _buffer = JceWriter().write_jce_struct(_buffer, 0)
    _buffer = JceWriter().write_map({'SvcReqGetDevLoginInfo': _buffer}, 0)
    _buffer = pack_head_no_token(info, _buffer, 'StatSvc.GetDevLoginInfo', 'StatSvc', 'SvcReqGetDevLoginInfo')
    _buffer = pack_(info, _buffer, types=11, encryption=1, sso_seq=info.seq)
    return _buffer


def GetDevLoginInfo_res(data):
    if data[0] == 120:
        data = zlib.decompress(data)
    data = un_jce_head(data)
    data = un_jce_head_2(data)
    stream = JceInputStream(data)
    s = JceStruct()
    s.read_from(stream)
    return s.to_json()
