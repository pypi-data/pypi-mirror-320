from and_tools import Pack, get_md5


def tlv_head(head, data):
    pack = Pack()
    pack.add_hex(head)
    pack.add_int(len(data), 2)
    pack.add_bin(data)
    return pack.get_bytes()


class TLV:
    def __init__(self, info):
        self.pack = Pack()
        self.info = info

    def T100(self, sso_version, app_id, app_client_version, sigmap):
        self.pack.empty()
        self.pack.add_hex('00 01')
        self.pack.add_int(sso_version)
        self.pack.add_int(app_id)
        self.pack.add_int(self.info.device.app_id)
        self.pack.add_int(app_client_version)
        self.pack.add_int(sigmap)
        _data = self.pack.get_bytes()
        return tlv_head('01 00', _data)

    def T10A(self, T0A: bytes):
        return tlv_head('01 0A', T0A)

    def T116(self, image_type=10):
        self.pack.empty()
        if self.info.device.client_type == 'Watch':
            self.pack.add_hex('00 00 F7 FF 7C 00 01 04 00 00')
        elif self.info.device.client_type == 'QQ':
            self.pack.add_int(image_type, 2)
            self.pack.add_hex('F7 FF 7C 00 01 04 00 01 5F 5E 10 E2')
        else:
            _data = b''
        _data = self.pack.get_bytes()
        return tlv_head('01 16', _data)

    def T143(self, T143: bytes):
        return tlv_head('01 43', T143)

    def T142(self):
        self.pack.empty()
        self.pack.add_body(self.info.device.package_name, 4)
        return tlv_head('01 42', self.pack.get_bytes())

    def T154(self):
        self.pack.empty()
        self.pack.add_int(self.info.seq)
        return tlv_head('01 54', self.pack.get_bytes())

    def T017(self, app_id: int, Uin: int, login_time: int):
        self.pack.empty()
        self.pack.add_hex('00 16 00 01')
        self.pack.add_hex('00 00 06 00')
        self.pack.add_int(app_id)
        self.pack.add_hex('00 00 00 00')
        self.pack.add_int(Uin)
        self.pack.add_hex('00 00 00 00')
        return tlv_head('00 17', self.pack.get_bytes())

    def T141(self):
        self.pack.empty()
        self.pack.add_hex('00 01')
        self.pack.add_body(self.info.device.internet, 2)
        self.pack.add_hex('00 02')
        self.pack.add_body(self.info.device.internet_type, 2)
        _data = self.pack.get_bytes()
        return tlv_head('01 41', _data)

    def T008(self):
        self.pack.empty()
        self.pack.add_hex('00 00 00 00 08 04 00 00')
        return tlv_head('00 08', self.pack.get_bytes())

    def T147(self):
        self.pack.empty()
        self.pack.add_hex('00 00 00 10')
        self.pack.add_body(self.info.device.version, 2, )
        self.pack.add_body(self.info.device.Sig, 2, True)
        _data = self.pack.get_bytes()
        return tlv_head('01 47', _data)

    def T177(self):
        self.pack.empty()
        self.pack.add_hex('01')
        self.pack.add_int(self.info.device.build_time)
        self.pack.add_body(self.info.device.sdk_version, 2)
        _data = self.pack.get_bytes()
        return tlv_head('01 77', _data)

    def T187(self):
        Mac = get_md5(self.info.device.Mac)
        self.pack.empty()
        self.pack.add_body(Mac, 2)
        _data = self.pack.get_bytes()
        return tlv_head('01 87', _data)

    def T188(self):
        _app_id = get_md5(str(self.info.device.app_id))

        self.pack.empty()
        self.pack.add_body(_app_id, 2)
        _data = self.pack.get_bytes()
        return tlv_head('01 88', _data)

    def T202(self):
        Bssid = get_md5(self.info.device.Bssid)
        self.pack.empty()
        self.pack.add_body(Bssid, 2)
        self.pack.add_body('<unknown ssid>', 2)
        _data = self.pack.get_bytes()
        return tlv_head('02 02', _data)

    def T511(self):
        """
            office.qq.com
            qun.qq.comgamecenter.qq.comdocs.qq.commail.qq.com	ti.qq.com
            vip.qq.com
            tenpay.comqqweb.qq.comqzone.qq.com
            mma.qq.comgame.qq.comopenmobile.qq.comconnect.qq.com"""

        domain = [
            'office.qq.com',
            'qun.qq.com',
            'gamecenter.qq.com',
            # 'graph.qq.com',
            # 'docs.qq.com',
            'mail.qq.com',
            'ti.qq.com',
            'vip.qq.com',
            # 'tenpay.com',
            'qqweb.qq.com',
            'qzone.qq.com',
            'mma.qq.com',
            'game.qq.com',
            # 'openmobile.qq.com',
            'connect.qq.com',
            'accounts.qq.com',
            # 'weishi.qq.com',

        ]
        self.pack.empty()
        self.pack.add_int(len(domain), 2)  # 数量
        for domain_result in domain:
            self.pack.add_hex('01')
            self.pack.add_body(domain_result, 2)

        return tlv_head('05 11', self.pack.get_bytes())
