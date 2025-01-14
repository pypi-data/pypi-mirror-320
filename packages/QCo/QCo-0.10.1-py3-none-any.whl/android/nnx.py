import datetime
import json
import random
import time

from box import Box
from loguru import logger

from and_tools import UnPack, TEA
from and_tools.device_infor import generate_china_imei, generate_china_mac, generate_china_bssid, \
    generate_random_device, generate_boot_id, generate_android_id
from android.Tcp import start_client, disconnect_client
from android.http.accounts import change_psw_getsms
from android.http.friends import Friends, bot_uin, delete_qq_friend
from android.http.level import GetLevelTask, qq_level_index, GetLevelStatus, RefreshTask
from android.http.music import Music
from android.http.qqsignin import WriteMindJar
from android.http.weishi import weishi_up_
from android.model import NNXInfo
from android.pack import *
from android.pack.SQQzoneSvc.delUgc import SQQzoneSvc_delUgc, SQQzoneSvc_delUgc_rsp
from android.pack.SQQzoneSvc.like import SQQzoneSvc_like, SQQzoneSvc_like_rsp
from android.pack.SQQzoneSvc.publishmood import SQQzoneSvc_publishmood, SQQzoneSvc_publishmood_rsp
from android.pack.SummaryCard import SummaryCard_ReqSummaryCard, SummaryCard_ReqSummaryCard_rsp
from android.pack.trpc_metaverse_mob_proxy_svr_MobProxy_SsoHandle import MobProxy_SsoHandle, MobProxy_SsoHandle_rsp
from android.struct.QQService import SvcReqGetDevLoginInfo, GetDevLoginInfo_profile, GetDevLoginInfo_res
from android.struct.SummaryCard import ReqSummaryCard
from android.utils import qq_bkn
from android.wlogin_sdk.wtlogin import wtlogin_exchange_emp, wtlogin_exchange_emp_rsp, trans_emp_auth, \
    trans_emp_auth_res


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

    def scan_code_auth(self, **kwargs):
        """扫码授权"""

        def req_func(info):
            return trans_emp_auth(info, **kwargs)

        def rsp_func(buffer):
            return trans_emp_auth_res(buffer, self.info, **kwargs)

        return self.tcp_task(req_func, rsp_func)

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

    def get_summary_card(self, Uin: int = None, ComeFrom: int = 0):
        """"
        获取自身卡片
            参数:
            Uin: int, optional
                目标用户uin 不填获取自身
            ComeFrom: int, optional
                来源 0=自己 1=其他 31=搜索

        """

        def req_func(info):
            _ComeFrom = ComeFrom

            if Uin is None:
                _Uin = info.uin
            else:
                _Uin = Uin
                if ComeFrom == 0:
                    _ComeFrom = 1  # 其他

            Buffer = ReqSummaryCard(
                Uin=_Uin,
                ComeFrom=_ComeFrom,  # 自身是0,别人是其他 暂时不管细节
                IsFriend=True,
                GetControl=69181,
                AddFriendSource=10004,
                # stLocaleInfo=User_Locale_Info,
                SecureSig=bytes.fromhex('00'),
                ReqMedalWallInfo=True,  # 勋章墙,
                ReqNearbyGodInfo=True,  # 附近的信息
                ReqExtendCard=True,  # 请求扩展卡
                RichCardNameVer=True  # 富卡名称验证

            ).to_bytes()
            return SummaryCard_ReqSummaryCard(info, Buffer)

        return self.tcp_task(req_func, SummaryCard_ReqSummaryCard_rsp)

    def q_zone_like(self, target_Uin: int, title: str, feedskey: str):
        """
        空间点赞
        """

        def req_func(info):
            return SQQzoneSvc_like(info, target_Uin, title, feedskey)

        return self.tcp_task(req_func, SQQzoneSvc_like_rsp)

    def Qzone_publishmood(self, content: str):
        """
        空间发布信息
            :content 发送的内容
        """

        def req_func(info):
            return SQQzoneSvc_publishmood(info, content)

        return self.tcp_task(req_func, SQQzoneSvc_publishmood_rsp)

    def qq_show_replace(self, show='女性带眼镜'):
        """
        更换QQ秀
            dict_keys(['女性带眼镜', '女性_紫星连衣裙', '女性_带口罩', '女性_兔兔发箍', '女性_元气针织帽', '女性_白色百褶裙'])


        """

        def req_func(info):
            return MobProxy_SsoHandle(info, show)

        def rsp_func(buffer):
            return MobProxy_SsoHandle_rsp(buffer, show)

        return self.tcp_task(req_func, rsp_func)

    def lv_continuous_login(self):

        self.get_summary_card()
        self.get_lv_task()

    def Qzone_delUgc(self, srcId: str):
        """
        空间删除信息
            :srcId 发送说说时会返回:tid
        """

        def req_func(info):
            return SQQzoneSvc_delUgc(info, srcId)

        return self.tcp_task(req_func, SQQzoneSvc_delUgc_rsp)

    def lv_Qzone(self, content=None):
        """空间任务"""
        content_list = [
            ' 小荷才露尖尖角，早有蜻蜓立上头',
            ' 有三秋桂子，十里荷花',
            ' 藕花珠缀，犹似汗凝妆',
            ' 一缕清香，一缕淡香',
            ' 接天莲叶无穷碧，映日荷花别样红',
            '能不能停下来，看看那个满眼泪花奔向你的我。',
            '承诺常常很像蝴蝶，美丽的盘旋后就不见了。'
        ]
        random_content = random.choice(content_list)
        if not content:
            content = random_content

        logger.info(f'空间任务内容：{content}')
        try:
            rsp = self.Qzone_publishmood(content).get('response', {})
            tid = rsp.get('Busi', {}).get('tid', '')
            self.get_qq_level()
            self.Qzone_delUgc(tid)
            task = self.refresh_task('2').get('response', {}).get('task', {})
            if not task:
                return Box(status=False, message='刷新任务异常')
            button_text = task.get('button_text')
            if button_text == '去领取':
                finished_accelerate_days = task.get('accelerate_days', 0)
            else:
                finished_accelerate_days = 0
            return Box(status=True, message=f'新增活跃天数{finished_accelerate_days}天',
                       finishedAccelerateDays=finished_accelerate_days)
        except Exception as e:
            return Box(status=False, message=f'空间任务异常{e}')

    def lv_clock_in(self):
        """打卡任务"""
        self.sign_in()
        self.refresh_task('3')

    def lv_weishi(self):
        self.weishi_up()
        self.get_lv_task()

    def lv_Friend(self):
        """加好友任务"""
        selected = random.sample(bot_uin, 3)
        try:
            Friend = Friends(self.info, self.get_bkn(), self.info.uin, self.get_cookie('qun.qq.com'))
            success = 0
            for f_uin in selected:
                rsp = Friend.del_friend(f_uin)
                if not rsp.status:
                    continue
                rsp = Friend.add_friend(f_uin)
                if not rsp.status:
                    continue
                success += 1
            task = self.refresh_task('1').get('response', {}).get('task', {})
            finished_accelerate_days = task.get('finished_accelerate_days', 0)
            return Box(status=True, message=f'新增活跃天数{finished_accelerate_days}天',
                       finishedAccelerateDays=finished_accelerate_days)

        except Exception as e:
            return Box(status=False, message=f'好友活跃任务异常{e}')

        finally:
            for f_uin in selected:
                delete_qq_friend(self.info, self.info.uin, f_uin, self.get_bkn(), self.get_cookie('qzone.qq.com'))

    def lv_music(self):
        """音乐任务"""
        try:

            self.Music_task()
            finished_accelerate_days = 0
            for i in range(15):
                logger.info('正在等待音乐任务完成，剩余次数{}'.format(20 - i))
                time.sleep(1)
                task = self.refresh_task('19').get('response', {}).get('task', {})
                button_text = task.get('button_text')
                if button_text == '已完成':
                    finished_accelerate_days = task.get('accelerate_days', 0)
                    break
            logger.success(f'音乐任务完成,新增活跃{finished_accelerate_days}天')
            return Box(status=True, message=f'新增活跃天数{finished_accelerate_days}天',
                       finishedAccelerateDays=finished_accelerate_days)

        except Exception as e:
            return Box(status=False, message=f'音乐任务异常{e}')

    def lv_cm_show(self):
        """"厘米秀装扮"""
        try:
            shows = ['女性带眼镜', '女性_紫星连衣裙', '女性_带口罩', '女性_兔兔发箍', '女性_元气针织帽',
                     '女性_白色百褶裙']
            for i in range(2):
                show = random.choice(shows)
                shows.remove(show)
                self.qq_show_replace(show)
            task = self.refresh_task('27').get('response', {}).get('task', {})
            if not task:
                return Box(status=False, message='刷新任务异常')
            button_text = task.get('button_text')
            if button_text == '已完成':
                finished_accelerate_days = task.get('accelerate_days', 0)
            else:
                finished_accelerate_days = 0
            return Box(status=True, message=f'新增活跃天数{finished_accelerate_days}天',
                       finishedAccelerateDays=finished_accelerate_days)
        except Exception as e:
            return Box(status=False, message=f'厘米秀任务异常{e}')

    def lv_extra_task_up(self, lv_music=True, zone_content=None):
        """升级所有额外任务"""
        rsp = self.exchange_emp()
        if rsp['status'] != 0:
            return Box(status=False, message='emp' + rsp['message'])
        rsp = self.no_tail_login()
        status = rsp['status']
        if status != 0:
            return Box(status=False, message=rsp['message'], status_int=status)

        task_functions = {
            '连续登录QQ': self.lv_continuous_login,
            '发布一条空间说说': lambda: self.lv_Qzone(content=zone_content),
            '去日签卡打一次卡': self.lv_clock_in,
            '去QQ音乐听歌30分钟+0.5天': self.lv_music,
            '加一位好友': self.lv_Friend,
            '去超级QQ秀更新装扮并保存': self.lv_cm_show,
            '去微视APP看视频': self.lv_weishi,
        }

        task_status = self.get_lv_task_status(True)
        execute_task = False
        for task_name, function in task_functions.items():

            if task_name == '去QQ音乐听歌30分钟+0.5天' and not lv_music:
                logger.info(f'{self.info.uin[:2]}跳过音乐')
                continue  # 如果任务是'去QQ音乐听歌30分钟+0.5天'并且设置为不可选执行，则跳过执行
            is_done = task_status.get(task_name, {}).get('is_done', None)
            if not is_done:
                logger.info(f'{self.info.uin[:2]}执行{task_name}')
                function()
                execute_task = True

        level = self.get_summary_card().get('response', {}).get('5', 0)
        if execute_task:
            task_status = self.get_lv_task_status(True)

        done_count = task_status.get('done_count', None)
        logger.info(f'{self.info.uin[:2]}已完成任务数量{done_count}')
        return Box(status=True, level=level, done_count=done_count, task_status=task_status)

    # http
    def get_bkn(self):
        """
        获取bkn
        :return:
        """
        return qq_bkn(self.info.cookies.skey)

    def get_lv_task(self):
        """获取等级任务"""
        return GetLevelTask(self.info, self.get_cookie("ti.qq.com"))

    def get_qq_level(self):
        """
        获取qq等级
        :return .get('levelInfo')
        """
        return qq_level_index(self.info, self.get_cookie("ti.qq.com"))

    def get_lv_task_status(self, query: bool = False):
        """获取等级任务状态"""
        return GetLevelStatus(self.info, self.get_cookie("ti.qq.com"), query)

    def refresh_task(self, task_id: str):
        """刷新任务状态"""
        return RefreshTask(self.info, self.get_cookie("ti.qq.com"), task_id)

    def sign_in(self):
        """签到"""
        return WriteMindJar(self.info, self.get_cookie("ti.qq.com"), self.info.cookies.skey)

    def weishi_up(self):
        """微视任务"""
        return weishi_up_(self.info)

    def change_psw_getsms(self, mobile):
        """修改密码，获取验证码
        :param mobile: 手机号
        """
        return change_psw_getsms(self.info, self.get_cookie("accounts.qq.com"), mobile)

    def Music_task(self):
        """音乐"""
        return Music(self.info).task()

    def get_clientkey(self, domain: str = 'https://qzone.qq.com'):
        """"
        获取客户端key
        :param domain: 域名
       """
        return f'https://ssl.ptlogin2.qq.com/jump?clientuin={self.info.uin}&clientkey={self.info.cookies.client_key}&keyindex=19&pt_mq=0&u1={domain}'

    def get_cookie(self, domain: str):
        """
        :param domain: 域名
        :return:
        """
        p_skey = self.info.cookies.p_skey.get(domain, None)
        if p_skey is None:
            return None
        return f"uin=o{self.info.uin}; skey={self.info.cookies.skey}; p_uin=o{self.info.uin}; p_skey={p_skey};"

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
        logger.error(f'不支持的mark{json_data["mark"]}')

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

    def close(self):
        clients_info = {}
        if self._tcp:
            clients_info = disconnect_client(self._tcp)
        return Box({'status': 0, 'message': 'AndroidQQ已释放', 'clients_info': clients_info})

    @property
    def tcp(self):
        return self._tcp
