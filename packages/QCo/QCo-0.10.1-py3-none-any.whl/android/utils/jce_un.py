from and_tools.Jce_b import JceReader


def un_jce_head(data) -> bytes:
    jce = JceReader(data)
    jce.read_int32(1)
    jce.read_int32(2)
    jce.read_int32(3)
    jce.read_int64(4)
    jce.read_string(5)
    jce.read_string(6)
    data = jce.read_any(7)
    return data


def un_jce_head_2(data) -> bytes:
    """Map"""
    jce = JceReader(data)
    jce.skip(1)  # ReadType
    jce.skip(2)  # ReadShort
    jce.read_string(0)
    jce.skip(1)  # ReadType
    jce.skip(2)  # ReadShort
    jce.read_string(0)
    data = jce.read_any(1)
    return data
