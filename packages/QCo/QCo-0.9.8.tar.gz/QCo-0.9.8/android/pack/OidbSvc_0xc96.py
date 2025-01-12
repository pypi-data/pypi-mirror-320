# 取消订阅
from google.protobuf.json_format import MessageToDict
from android.im.oidb.OidbSvc_0xc96 import ReqBody, UnfollowReq, UnFollowExt, RspBody
from android.im.oidb.oidb_sso import OIDBSSOPkg
from android.utils import pack_head_no_token, pack_


def OidbSvc_0xc96(info, puin: int, cmd_type: int) -> bytes:
    reqBody = ReqBody(
        puin=puin,  # ,3
        cmd_type=cmd_type,  # 4
        unfollow_req=UnfollowReq(
            # 12
            ext=UnFollowExt(
                source_from=1  # 来源?
            )
        )
    )
    oIDBSSOPkg = OIDBSSOPkg(
        command=3222,
        service_type=0,
        result=0,
        bodybuffer=reqBody.SerializeToString(),
    )
    buffer = oIDBSSOPkg.SerializeToString()

    buffer = pack_head_no_token(info, buffer, 'OidbSvc.0xc96')
    buffer = pack_(info, buffer, types=11, encryption=1, sso_seq=info.seq)
    return buffer


def OidbSvc_0xc96_rsp(buffer: bytes):
    oIDBSSOPkg = OIDBSSOPkg()
    oIDBSSOPkg.ParseFromString(buffer)
    rep_body = RspBody()
    rep_body.ParseFromString(oIDBSSOPkg.bodybuffer)
    return MessageToDict(rep_body)


if __name__ == '__main__':
    pass
