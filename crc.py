def calculate_crc(data: bytes) -> int:
    """Calculate CRC-16-CCITT using polynomial 0x1021."""
    crc = 0xFFFF

    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    return crc


def verify_crc(data: bytes, crc: int) -> bool:
    """Return True when the calculated CRC matches the transmitted CRC."""
    return calculate_crc(data) == crc
