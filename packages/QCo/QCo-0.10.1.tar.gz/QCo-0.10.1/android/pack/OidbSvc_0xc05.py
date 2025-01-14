# 获取授权列表包
from google.protobuf.json_format import MessageToDict

from android.im.oidb.oidb_0xc05 import GetAuthAppListReq, ReqBody, RspBody
from android.im.oidb.oidb_sso import OIDBSSOPkg
from android.utils import pack_head_no_token, pack_


def OidbSvc_0xc05(info, start: int, limit: int):
    getAuthAppListinfoReq = GetAuthAppListReq(
        start=start,
        limit=limit
    )
    req_body = ReqBody(
        get_auth_app_list_req=getAuthAppListinfoReq
    )
    oIDBSSOPkg = OIDBSSOPkg(
        command=3077,
        result=0,
        service_type=1,
        bodybuffer=req_body.SerializeToString(),
    )
    buffer = oIDBSSOPkg.SerializeToString()
    buffer = pack_head_no_token(info, buffer, 'OidbSvc.0xc05')
    buffer = pack_(info, buffer, types=11, encryption=1, sso_seq=info.seq)
    return buffer


def OidbSvc_0xc05_rep(buffer):
    oIDBSSOPkg = OIDBSSOPkg()
    oIDBSSOPkg.ParseFromString(buffer)
    rep_body = RspBody()
    rep_body.ParseFromString(oIDBSSOPkg.bodybuffer)
    return MessageToDict(rep_body)
