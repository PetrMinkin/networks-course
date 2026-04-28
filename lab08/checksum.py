def find_checksum(data):
    if len(data) % 2 != 0:
        data = data + b'\x00'
    checksum = 0
    for i in range(0, len(data), 2):
        two_bytes = data[i]*(2**8) + data[i + 1]
        checksum += two_bytes
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & (2**16-1)

def check_checksum(data, checksum):
    checksum_bytes = checksum.to_bytes(2, byteorder='big')
    return find_checksum(checksum_bytes+data)==0 #тут два лишних обращения числа до 1 типа


if __name__ == "__main__":
    data = b"10000001"
    assert check_checksum(data, 15934)

    data = b"0000"
    assert check_checksum(data, 40863)

    data = b"101010101010101001"
    assert check_checksum(data, 17997)

    assert check_checksum(data, find_checksum(data))