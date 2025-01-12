import datetime
import json
import time

from box import Box
from loguru import logger
from and_tools import UnPack, TEA
from and_tools.device_infor import generate_china_imei, generate_china_mac, generate_china_bssid, \
    generate_random_device, generate_boot_id, generate_android_id
from android.Tcp import start_client
from android.model import NNXInfo
from android.model.nnx_info import Device
from android.pack import *
from android.struct.QQService import SvcReqGetDevLoginInfo, GetDevLoginInfo_profile, GetDevLoginInfo_res
from android.wlogin_sdk.wtlogin import wtlogin_exchange_emp, wtlogin_exchange_emp_rsp


class AndroidNNX:
    def __init__(self, proxy=None):
        if proxy is None:
            proxy = []

        self.info = NNXInfo()
        self.pack_list = {}  # 用于存储包的字典
        self._tcp = start_client(_func=self.un_data, proxy=proxy)

    def Tcp_send(self, data):
        self._tcp.sendall(data)
        start_time = time.time()  # 获取当前时间
        seq = self.info.seq
        while time.time() - start_time < 3:  # 检查是否已过去三秒
            data = self.pack_list.get(seq)
            if data is not None:
                self.pack_list.pop(seq)  # 删除已经取出的包
                break
            time.sleep(0.1)
        self.info.seq = seq + 1
        return data

    def tcp_task(self, req_func, rsp_func):
        buffer = req_func(self.info)
        if not self._tcp:
            return Box(status=-1, message='没有成功连接到服务器')

        buffer = self.Tcp_send(buffer)
        if buffer == b'':
            if self.info.Tips is not None:
                status = -99
                message = self.info.Tips
            else:
                status = -91
                message = '返回空包体'
            return Box(status=status, message=message)
        elif buffer is None:
            return Box(status=-1, message='未返回数据')
        response = rsp_func(buffer)
        return Box(status=0, message='请求成功', response=response)

    def un_data(self, data):
        """解包"""
        pack = UnPack(data)
        pack.get_int()
        pack_way = pack.get_byte()

        pack.get_byte()  # 00
        _len = pack.get_int()
        pack.get_bin(_len - 4)  # Uin bin
        _data = pack.get_all()
        if pack_way == 2:
            # 登录相关
            _data = TEA.decrypt(_data, '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00')
        elif pack_way == 1:
            _data = TEA.decrypt(_data, self.info.share_key)
        else:
            _data = b''
            logger.info('未知的解密类型')

        if not _data:
            return
        else:
            pack = UnPack(_data)
            _len = pack.get_int()
            part1 = pack.get_bin(_len - 4)
            _len = pack.get_int()
            part2 = pack.get_bin(_len - 4)
            # part1
            pack = UnPack(part1)
            seq = pack.get_int()
            pack.get_int()
            _len = pack.get_int()
            Tips = pack.get_bin(_len - 4).decode('utf-8')
            _len = pack.get_int()
            Cmd = pack.get_bin(_len - 4).decode('utf-8')
            # print('包序号', seq, '包类型', Cmd, part2.hex())
            if Tips != '':
                seq = self.info.seq  # 推送到最后一个包
                self.info.Tips = Tips
                # log.warning(f'Tips:{Tips}')
            # part2
            # log.info('包序号', ssoseq, '包类型', Cmd, part2.hex())
            if 0 < seq < 1000000:
                # log.info('包序号', seq, '包类型', Cmd, part2.hex())
                self.pack_list.update({seq: part2})
            else:
                # log.info('推送包', seq, '包类型', Cmd, part2.hex())
                pass

    # 功能包
    def no_tail_login(self):
        """无尾登录包"""

        def req_func(info):
            return OidbSvc_0x88d_1(info, 790038285)

        return self.tcp_task(req_func, OidbSvc_0x88d_1_rep)

    def get_auth_list(self, start: int = 0, limit: int = 10):
        """
        获取授权列表
            参数:
                start = 0
                limit= 10
        """

        def req_func(info):
            return OidbSvc_0xc05(info, start, limit)

        return self.tcp_task(req_func, OidbSvc_0xc05_rep)

    def get_dev_login_info(self, iGetDevListType: int = 7):
        """
        获取设备登录信息
        参数:
            iGetDevListType: int, optional
                设备列表类型。如果未指定，将使用默认值 7。

        """

        def req_func(info):
            item = SvcReqGetDevLoginInfo(
                vecGuid=self.info.guid,
                iTimeStamp=1,
                strAppName='com.tencent.mobileqq',
                iRequireMax=20,
                iGetDevListType=iGetDevListType

            )
            return GetDevLoginInfo_profile(info, item)

        return self.tcp_task(req_func, GetDevLoginInfo_res)

    def unsubscribe(self, p_uin: int, cmd_type: int = 2):
        """
        取消订阅
            参数:
                p_uin: int 目标
                    2720152058 QQ团队
                    1770946116 安全中心
                    2290230341 QQ空间动态
                    2747277822 QQ手游
                    2010741172 QQ邮箱提醒


                cmd_type: int 默认2
        """

        def req_func(info):
            return OidbSvc_0xc96(info, p_uin, cmd_type)

        return self.tcp_task(req_func, OidbSvc_0xc96_rsp)

    def exchange_emp(self, forcibly: bool = False):
        """更新缓存"""
        if self.info.emp_time and not forcibly:
            last_emp_time = datetime.datetime.strptime(self.info.emp_time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.datetime.now()
            time_difference = current_time - last_emp_time
            if time_difference < datetime.timedelta(hours=12):
                # 12个小时内不更新
                return {'status': 0, 'message': '无需更新'}

        def req_func(info):
            return wtlogin_exchange_emp(info)

        def rsp_func(buffer):
            return wtlogin_exchange_emp_rsp(self.info, buffer)

        return self.tcp_task(req_func, rsp_func)

    # Tools
    def set_token_a(self, data):
        """
        设置TokenA
        """
        json_data = json.loads(data)
        if json_data['mark'] == 1013:

            self.info = NNXInfo.model_validate(json_data)
            default_values = {
                'self.info.device.Imei': generate_china_imei,
                'self.info.device.boot_id': generate_boot_id,
                'self.info.device.Bssid': generate_china_bssid,
                'self.info.device.Mac': generate_china_mac,
                'self.info.device.android_id': generate_android_id,
                'self.info.device.model': lambda: device_info.get('model'),
                'self.info.device.brand': lambda: device_info.get('brand'),
                'self.info.UN_Tlv_list.wtSessionTicket': lambda: bytes.fromhex(
                    '8EED6A0746FD906D06512F5F074BAD0F2D1729FA106EE98D40C9A5221F367579703360E29F4B7D4AE7FC25AE2D8DF241'
                ),
                'self.info.UN_Tlv_list.wtSessionTicketKey': lambda: bytes.fromhex(
                    '04BEBF0116413CF54C3D21919F0164D8'
                ),
            }

            device_info = generate_random_device()  # 生成随机设备
            for field, default in default_values.items():
                if not eval(field):
                    logger.warning(f'丢失{field}')
                    exec(f"{field} = default()")

                # 暂时固定
            self.info.device.sdk_version = '6.0.0.2497'
            self.info.device.package_name = 'com.tencent.mobileqq'
            self.info.device.build_time = 1645432578
            self.info.device.Sig = 'A6 B7 45 BF 24 A2 C2 77 52 77 16 F6 F3 6E B6 8D'
            self.info.device.version = '8.8.85'
            self.info.device.sdk_version = '6.0.0.2497'
            self.info.device.var = '||A8.9.71.9fd08ae5'

            return

        json_data = json.loads(data)
        self.info.uin = str(json_data['UIN'])

        self.info.share_key = bytes.fromhex(json_data['Sharekey'].replace(' ', ''))
        self.info.guid = bytes.fromhex(json_data['Guid'])
        self.info.device.app_id = int(json_data.get('Appid', self.info.device.app_id))
        self.info.UN_Tlv_list.TGT_T10A = bytes.fromhex(json_data['TGT'])
        self.info.UN_Tlv_list.D2_T143 = bytes.fromhex(json_data['D2'])
        self.info.UN_Tlv_list.userSt_Key = bytes.fromhex(json_data.get('userSt_Key', ''))
        self.info.UN_Tlv_list.userStSig = bytes.fromhex(json_data.get('userStSig', ''))
        self.info.UN_Tlv_list.wtSessionTicket = bytes.fromhex(json_data['wtSessionTicket'])
        self.info.UN_Tlv_list.wtSessionTicketKey = bytes.fromhex(json_data['wtSessionTicketKey'])

        if not self.info.UN_Tlv_list.wtSessionTicket:
            self.info.UN_Tlv_list.wtSessionTicket = bytes.fromhex(
                '8EED6A0746FD906D06512F5F074BAD0F2D1729FA106EE98D40C9A5221F367579703360E29F4B7D4AE7FC25AE2D8DF241')
        if not self.info.UN_Tlv_list.wtSessionTicketKey:
            self.info.UN_Tlv_list.wtSessionTicketKey = bytes.fromhex(
                '04BEBF0116413CF54C3D21919F0164D8')
        self.info.emp_time = json_data.get('emp_time')

        if json_data.get('cookies', None) is None:
            return

        self.info.cookies.skey = json_data['cookies'].get('skey', '')
        self.info.cookies.p_skey = json_data['cookies'].get('p_skey', {})
        self.info.cookies.client_key = json_data.get('cookies', {}).get('client_key', '')

        device_info_defaults = {
            'Imei': generate_china_imei,
            'Mac': generate_china_mac,
            'Bssid': generate_china_bssid,
            'model': lambda: generate_random_device().get('model'),
            'brand': lambda: generate_random_device().get('brand'),
            'boot_id': generate_boot_id,
            'android_id': lambda: generate_android_id(),
        }

        for attr, generator in device_info_defaults.items():
            value = json_data.get("device", {}).get(attr, None)

            if value is None:  # 判断值是否为 None
                if attr not in json_data.get("device", {}):
                    print(f"缺少设备信息字段：{attr}，使用生成的默认值")
                if attr in ['model', 'brand']:  # 特殊处理依赖其他生成器的字段
                    device = generate_random_device()
                    self.info.device.brand = device['brand']
                    self.info.device.model = device['model']
                else:
                    value = generator()

            setattr(self.info.device, attr, value)
        # 暂时固定
        self.info.device.sdk_version = '6.0.0.2497'
        self.info.device.package_name = 'com.tencent.mobileqq'
        self.info.device.build_time = 1645432578
        self.info.device.Sig = 'A6 B7 45 BF 24 A2 C2 77 52 77 16 F6 F3 6E B6 8D'
        self.info.device.version = '8.8.85'
        self.info.device.sdk_version = '6.0.0.2497'
        self.info.device.var = '||A8.9.71.9fd08ae5'

    def get_token_a(self):
        tokenA = {
            'uin': self.info.uin,
            'guid': self.info.guid.hex(),
            'share_key': self.info.share_key.hex(),
            'device': {
                'app_id': self.info.device.app_id,
                'Imei': self.info.device.Imei,
                'boot_id': self.info.device.boot_id,
                'Bssid': self.info.device.Bssid,
                'Mac': self.info.device.Mac,
                'android_id': self.info.device.android_id,
                'model': self.info.device.model,
                'brand': self.info.device.brand,

            },
            'UN_Tlv_list': {
                'TGT_T10A': self.info.UN_Tlv_list.TGT_T10A.hex(),
                'D2_T143': self.info.UN_Tlv_list.D2_T143.hex(),
                'userSt_Key': self.info.UN_Tlv_list.userSt_Key.hex(),
                'userStSig': self.info.UN_Tlv_list.userStSig.hex(),
                'wtSessionTicket': self.info.UN_Tlv_list.wtSessionTicket.hex(),
                'wtSessionTicketKey': self.info.UN_Tlv_list.wtSessionTicketKey.hex(),
            },
            'cookies': self.info.cookies.__dict__,
            'emp_time': self.info.emp_time,
            'mark': 1013,  # 解析标识
        }
        return json.dumps(tokenA)

    @property
    def tcp(self):
        return self._tcp
