import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from android import AndroidNNX

N = AndroidNNX()
N.set_token_a(
    '{"uin": "3947364059", "guid": "b7e0bd22f75a0244d6e07297f5c37ac3", "share_key": "662c6b3d2c767542246e7d44725e5768", "device": {"app_id": 537254355, "Imei": "868731458689198", "boot_id": "37e828e4-5a3d-422d-9ac0-2b094a2e27f4", "Bssid": "9C:D2:1E:31:B6:DA", "Mac": "F4:F2:6D:D3:B6:7E", "android_id": "539c2fabc87a71f5", "model": "Nova 10", "brand": "Huawei"}, "UN_Tlv_list": {"TGT_T10A": "e14848a20fd755596acb4975b1da548675bb97b6a6170db7e0abe019135b22399c1c2383f45f2f338e16e44868018c7adb97e54b0279c686c9efbc5605f25817d941499b9bb3b878", "D2_T143": "1f2587ba5396aa3c8c245f2b8996d8946264b1d888b7a6243f75ee2c1345fb98b28f61d7979bc3fbfe6fdd4685b56b9ca52b9f9a97df5ac23903aa11a491f5c3", "userSt_Key": "4d4079604034596e3b3f69485a417874", "userStSig": "0001678371e50058fcd04771d2ddde73de5120ed6ad070baed09c0aa3a3346144be3cc3ea0b941b4a5ac77fe1812a1c228c6fe65b2645d69e7d86e0f4e6f9353624b6f5aa74c92d916a2d525f50740edc265eefea95729efd26ee9801451c1c9", "wtSessionTicket": "3afab6783d583debb00a3cfcc7415cddd2fc6ac0d57301210ce0c3902787ce3b9d10a5656b7e50534d8e240a0ba5011a", "wtSessionTicketKey": "5770f38b1a656aa0a8aad1c3feeaba17"}, "cookies": {"skey": "M3aWh9oTZX", "client_key": "28fa66c72037dbbad0e0e8e9db75c3614175939a3e886398662d6dacc975290bec2486eb2326692785d1677c581ea16c", "p_skey": {"office.qq.com": "My*7NP77SGdrE-6AztPrADSh7fGBskFBJQdJogI8njE_", "qun.qq.com": "F3a5IVQjNL6XwvWJJUoxsxfu1RG98KhmwmamCb8uL6Q_", "gamecenter.qq.com": "rUCiClZlfVoXs8dQexGYWZyi1H3-EW0LHD9ASrS3fNk_", "mail.qq.com": "*5Oy0eFHKZd-MlZu0EVoMwvnwjJN2eAE4s8kNhE5GqM_", "ti.qq.com": "hnAKJ3s5vhkTtjt9knKvvRYpykfv10kqdyGcqwPN*1I_", "vip.qq.com": "F99TvZID85gNPQpdOMrqbK5abbGk9h3V2WBYcW9eZrE_", "qqweb.qq.com": "DQjWR4KZTjAbgFgGGv99u6JZmuWKh0bOubWrARqDFMc_", "qzone.qq.com": "v8c2bjwgfTUvLobUOFOPOh*wTSc59EKFvxNBnsx4tZQ_", "mma.qq.com": "pYXhWMEI9TNtQ4-hrHisxnCj*E1X6tnpKR5UK2jrGd0_", "game.qq.com": "OlqiJ*tzdeBInEJ-jd2*17sPF0ClrWLGN4j-lboXPwE_", "connect.qq.com": "osHIOQBOULW66wIqbjVXyqmQHLxXnogHnxby96afdmI_", "accounts.qq.com": "QTU0x11UMWE2kbxuTV4e*yFPGydoJ7gL5nEdYF7sQss_"}}, "emp_time": "2025-01-12 15:40:19", "mark": 1013}')
print(N.no_tail_login())
# print(N.exchange_emp())
print(N.get_token_a())
# print(N.get_dev_login_info())
# print(N.get_auth_list())

# print(generate_random_device())
# print(generate_china_mac())
