def calculate_checksum(data: bytes) -> int:
    """Calculate a standard 16-bit Internet-style one's-complement checksum."""
    total = 0
if len(data) % 2 == 1:
    
        data += b"\x00"

    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        total += word
        total = (total & 0xFFFF) + (total >> 16)

    return (~total) & 0xFFFF


def verify_checksum(data: bytes, checksum: int) -> bool:
    """Return True when the calculated checksum matches the transmitted checksum."""
    return calculate_checksum(data) == checksum
