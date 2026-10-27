import random


class WirelessChannel:
    """Software-only noisy channel with targeted checksum/CRC stress errors."""

    def __init__(self, error_rate=0.05, seed=2026):
        if not 0 <= error_rate <= 1:
            raise ValueError("error_rate must be between 0 and 1.")
        self.error_rate = error_rate
        self.random = random.Random(seed)
        self._crc_masks = {}

    @staticmethod
    def _crc_step(crc, byte):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
        return crc

    @classmethod
    def _crc_value(cls, data):
        crc = 0xFFFF
        for byte in data:
            crc = cls._crc_step(crc, byte)
        return crc

    def _crc_cancelling_mask(self, length):
        """Build a non-zero error mask that leaves CRC-16 unchanged.

        CRC is linear apart from its fixed initial state. Therefore a mask
        whose CRC equals the CRC of an all-zero message of the same length
        produces no CRC change when XORed with any message of that length.
        The mask is deliberately chosen so that the Internet checksum changes,
        allowing the Hybrid scheme to reject the packet even when CRC passes.
        """
        if length in self._crc_masks:
            return self._crc_masks[length]
        if length < 4:
            return None

        target = self._crc_value(bytes(length))
        prefix = bytearray(length)
        prefix[0] = 1

        crc = 0xFFFF
        for byte in prefix[:-2]:
            crc = self._crc_step(crc, byte)

        for suffix in range(65536):
            high = suffix >> 8
            low = suffix & 0xFF
            final_crc = self._crc_step(self._crc_step(crc, high), low)
            if final_crc == target:
                mask = bytes(prefix[:-2] + bytearray([high, low]))
                self._crc_masks[length] = mask
                return mask
        return None

    def _checksum_cancelling_error(self, received):
        """Flip equal-valued bits in two 16-bit words so checksum is unchanged."""
        usable_length = len(received) - (len(received) % 2)
        words = [((received[i] << 8) | received[i + 1])
                 for i in range(0, usable_length, 2)]
        candidates = []
        for bit in range(16):
            zero_words = [i for i, word in enumerate(words) if not (word & (1 << bit))]
            one_words = [i for i, word in enumerate(words) if word & (1 << bit)]
            if zero_words and one_words:
                candidates.append((bit, zero_words, one_words))
        if not candidates:
            return False
        bit, zero_words, one_words = self.random.choice(candidates)
        indexes = [self.random.choice(zero_words), self.random.choice(one_words)]
        for index in indexes:
            words[index] ^= 1 << bit
            received[index * 2] = (words[index] >> 8) & 0xFF
            received[index * 2 + 1] = words[index] & 0xFF
        return True

    def _crc_cancelling_error(self, received):
        mask = self._crc_cancelling_mask(len(received))
        if mask is None:
            return False
        for i, value in enumerate(mask):
            received[i] ^= value
        return True

    def transmit(self, data: bytes):
        """Return received bytes, corruption flag, and error-pattern label."""
        received = bytearray(data)
        if self.random.random() >= self.error_rate:
            return bytes(received), False, "none"
        if len(received) < 4:
            return bytes(received), False, "too-short"

        error_type = self.random.choices(
            ["single-bit", "multiple-bit", "burst",
             "checksum-cancelling", "crc-cancelling"],
            weights=[40, 25, 15, 10, 10], k=1
        )[0]

        if error_type == "checksum-cancelling":
            if not self._checksum_cancelling_error(received):
                error_type = "multiple-bit"

        if error_type == "crc-cancelling":
            if not self._crc_cancelling_error(received):
                error_type = "multiple-bit"

        if error_type == "single-bit":
            pos = self.random.randrange(len(received) * 8)
            received[pos // 8] ^= 1 << (pos % 8)
        elif error_type == "multiple-bit":
            flips = min(self.random.randint(2, 8), len(received) * 8)
            for pos in self.random.sample(range(len(received) * 8), flips):
                received[pos // 8] ^= 1 << (pos % 8)
        elif error_type == "burst":
            max_len = min(16, len(received) * 8)
            burst_length = self.random.randint(2, max_len)
            start = self.random.randrange(len(received) * 8 - burst_length + 1)
            for pos in range(start, start + burst_length):
                received[pos // 8] ^= 1 << (pos % 8)

        return bytes(received), True, error_type
