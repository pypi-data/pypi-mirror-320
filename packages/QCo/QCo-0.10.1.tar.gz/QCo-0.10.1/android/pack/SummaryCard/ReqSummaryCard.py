# struct SummaryCard;
import json
import zlib

from and_tools.Jce import JceInputStream, JceStruct
from and_tools.Jce_b import JceWriter, JceReader

from android.utils import pack_head_no_token, pack_, un_jce_head
from android.struct.SummaryCard import ReqSummaryCard


def SummaryCard_ReqSummaryCard(info, Buffer):
    """获取摘要卡"""

    Buffer = JceWriter().write_jce_struct(Buffer, 0)

    Buffer = JceWriter().write_map({'ReqHead': bytes.fromhex('0A 00 02 0B'), 'ReqSummaryCard': Buffer},
                                   0)  # 似乎新版有更多的验证,因此用旧的头部

    Buffer = pack_head_no_token(info, Buffer, 'SummaryCard.ReqSummaryCard',
                                'SummaryCardServantObj', 'ReqSummaryCard')
    Buffer = pack_(info, Buffer, types=11, encryption=1, sso_seq=info.seq)
    return Buffer


def SummaryCard_ReqSummaryCard_rsp(Buffer):
    if Buffer[0] == 120:
        Buffer = zlib.decompress(Buffer)

    data = un_jce_head(Buffer)
    _map = JceReader(data).read_map(0)
    _dict = _map.get('RespSummaryCard', None)
    if _dict is None:
        return None
    # 包体太大了,自动解析
    RespSummaryCard = _dict['SummaryCard.RespSummaryCard']
    stream = JceInputStream(RespSummaryCard)
    jce = JceStruct()
    jce.read_from(stream)
    return json.loads(jce.to_json())


if __name__ == '__main__':
    pass
