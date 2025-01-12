import random
import uuid


def calculate_luhn(partial_imei):
    """
    Calculate the Luhn checksum digit for a given IMEI prefix.

    Args:
        partial_imei (str): The first 14 digits of the IMEI.

    Returns:
        int: The Luhn checksum digit.
    """
    total = 0
    for i, digit in enumerate(partial_imei):
        n = int(digit)
        if i % 2 == 1:  # Double every second digit
            n *= 2
            if n > 9:  # Subtract 9 from numbers larger than 9
                n -= 9
        total += n
    return (10 - (total % 10)) % 10


def generate_china_imei():
    """
   生成一个适用于中国地区的随机有效IMEI号码。

    返回：
        str：一个带有中国特定TAC的有效IMEI号码。
    """
    # Select a TAC prefix commonly used in China
    china_tac_prefixes = [
        "860206",  # Example TAC for Chinese devices
        "867600",  # Example TAC for Huawei devices
        "868731",  # Example TAC for Xiaomi devices
        "861234"  # Example TAC for other Chinese brands
    ]
    tac = random.choice(china_tac_prefixes)

    # Generate the next 8 random digits (6 device + 2 variant)
    device_identifier = ''.join(str(random.randint(0, 9)) for _ in range(8))

    # Combine TAC and random device identifier to form the first 14 digits
    partial_imei = tac + device_identifier

    # Calculate the checksum digit
    checksum = calculate_luhn(partial_imei)

    # Append the checksum digit
    full_imei = partial_imei + str(checksum)
    return full_imei


def generate_china_mac():
    """
    生成一个带有中国基础 OUI 前缀的随机 MAC 地址。

    返回：
        str：一个有效的 MAC 地址。
    """
    # List of China-based OUI prefixes
    china_oui_prefixes = [
        "00:25:9E",  # Huawei
        "EC:26:CA",  # Huawei
        "74:23:44",  # Xiaomi
        "EC:3E:09",  # Xiaomi
        "00:17:EB",  # ZTE
        "9C:D2:1E",  # ZTE
        "C4:6E:1F",  # TP-Link
        "F4:F2:6D"  # TP-Link
    ]

    # Choose a random OUI prefix
    oui = random.choice(china_oui_prefixes)

    # Generate the remaining 3 bytes of the MAC address
    remaining_bytes = ":".join(f"{random.randint(0, 255):02X}" for _ in range(3))

    # Combine OUI and the remaining bytes
    mac_address = f"{oui}:{remaining_bytes}"
    return mac_address


def generate_china_bssid():
    """
    生成一个带有中国区域唯一标识符（OUI）前缀的随机BSSID。

    返回：
        str：一个有效的BSSID。
    """
    # List of China-based OUI prefixes for BSSID
    china_oui_prefixes = [
        "00:25:9E",  # Huawei
        "EC:26:CA",  # Huawei
        "74:23:44",  # Xiaomi
        "EC:3E:09",  # Xiaomi
        "00:17:EB",  # ZTE
        "9C:D2:1E",  # ZTE
        "C4:6E:1F",  # TP-Link
        "F4:F2:6D"  # TP-Link
    ]

    # Randomly select an OUI prefix
    oui = random.choice(china_oui_prefixes)

    # Generate the remaining 3 bytes of the BSSID
    remaining_bytes = ":".join(f"{random.randint(0, 255):02X}" for _ in range(3))

    # Combine the OUI and the remaining bytes
    bssid = f"{oui}:{remaining_bytes}"
    return bssid


def generate_random_device():
    """
    生成一个随机设备的品牌和型号。

    返回:
        dict: 一个包含随机品牌和型号的字典。
    """
    # Define brands and their corresponding models
    device_data = {
        "Samsung": ["Galaxy S22", "Galaxy Note 20", "Galaxy Z Fold4", "Galaxy A52", "Galaxy Tab S8"],
        "Xiaomi": ["Redmi Note 12", "Mi 11", "Poco X4", "Mi Pad 5", "Redmi K50"],
        "Huawei": ["P50 Pro", "Mate 50", "Nova 10", "Honor 70", "MatePad Pro"],
        "OnePlus": ["9 Pro", "Nord 2", "10T", "OnePlus 11", "OnePlus 8T"],
        "Sony": ["Xperia 1 III", "Xperia 5 IV", "Xperia 10 III", "Xperia Pro-I"],
        "Google": ["Pixel 6", "Pixel 7 Pro", "Pixel 5a", "Pixel Slate", "Pixelbook Go"],
    }

    # Randomly select a brand
    brand = random.choice(list(device_data.keys()))

    # Randomly select a model from the chosen brand
    model = random.choice(device_data[brand])

    # Return the random brand and model
    return {"brand": brand, "model": model}


def generate_boot_id():
    """
    生成一个随机的 boot_id 使用 UUID4。

    返回:
    str: 一个随机生成的 boot_id。
    """
    return str(uuid.uuid4())


def generate_android_id():
    """
    生成一个随机的Android ID。
    """
    return ''.join(random.choices('0123456789abcdef', k=16))
