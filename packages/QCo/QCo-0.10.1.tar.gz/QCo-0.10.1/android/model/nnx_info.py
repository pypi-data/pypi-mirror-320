# 数据结构
import time
from typing import Union
from pydantic import BaseModel, field_validator, model_validator

from and_tools import get_random_bin


class Cookies(BaseModel):
    skey: str = None
    client_key: str = None
    p_skey: dict = None


class UnTlvList(BaseModel):
    TGT_T10A: bytes = b''
    D2_T143: bytes = b''
    T100_qr_code_mark: bytes = b''  # watch
    T018: bytes = b''  # watch
    T019: bytes = b''  # watch
    T065: bytes = b''  # watch
    T108: bytes = b''
    userSt_Key: bytes = b''  # T10E
    wtSessionTicketKey: bytes = b''  # 134
    wtSessionTicket: bytes = b''  # 133

    userStSig: bytes = b''  # T114
    T16A: bytes = b''
    T106: bytes = b''
    T146: Union[str, dict] = None
    T192_captcha: str = None
    T104_captcha: bytes = b''
    T546_captcha: bytes = b''

    @model_validator(mode="before")
    @classmethod
    def validate_hex_fields(cls, values):
        for field in ['TGT_T10A',
                      'D2_T143',
                      'userSt_Key',
                      'userStSig',
                      'wtSessionTicket',
                      'wtSessionTicketKey']:
            if isinstance(values.get(field), str):
                values[field] = bytes.fromhex(values[field])
        return values


class Device(BaseModel):
    # 软件信息
    version: str = None
    package_name: str = None  # com.tencent.qqlite
    Sig: str = None
    build_time: int = None  # 软件构建时间 1654570540
    sdk_version: str = None  # #6.0.0.2366
    client_type: str = 'QQ'  # android
    app_id: int = None  # 似乎可以传空
    var: str = None
    # 设备信息
    name: str = 'android'
    internet: str = 'China Mobile GSM'
    internet_type: str = 'wifi'
    model: str = None
    brand: str = None
    Mac_bytes: bytes = None
    Bssid_bytes: bytes = None
    android_id: str = None  # Android 操作系统中设备的一个唯一ID。每个设备在首次启动时都会生成一个随机的64位数字作为其
    boot_id: str = None  # Linux系统中用来唯一标识系统自上次启动以来的运行时期的标识符
    Imei: str = None
    Mac: str = None
    Bssid: str = None


class NNXInfo(BaseModel):
    uin: str = None
    uin_name: str = None
    password: str = None
    seq: int = 5266
    share_key: bytes = None  # _D2Key
    key_rand: bytes = get_random_bin(16)
    key_tgtgt: bytes = None
    key_Pubkey: bytes = None  # 公钥
    guid: bytes = get_random_bin(16)
    login_time: int = int(time.time())
    UN_Tlv_list: UnTlvList = UnTlvList()
    device: Device = Device()
    cookies: Cookies = Cookies()
    Tips: str = None
    proxy_str: str = None
    proxy_proxies: dict = None
    emp_time: str = None

    @model_validator(mode="before")
    @classmethod
    def validate_hex_fields(cls, values):
        for field in ['share_key', 'guid']:
            if isinstance(values.get(field), str):
                values[field] = bytes.fromhex(values[field])
        return values
