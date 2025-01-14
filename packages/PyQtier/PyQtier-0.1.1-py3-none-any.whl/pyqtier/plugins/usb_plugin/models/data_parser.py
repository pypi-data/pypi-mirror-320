from typing import Optional, Callable


class UsbDataParser(object):
    def __init__(self):
        self._callback_after_parsing: Optional[Callable] = None

    def set_callback_after_parsing(self, callback: Callable):
        if callable(callback):
            self._callback_after_parsing = callback
        else:
            raise TypeError("Callback must be callable")

    def parse(self, data):
        """
        Do not forget calling callback after processing data if you rewrite parser
        :param data: obtained encoded data
        :return: decoded and processed data
        """
        data.decode()

    def parse_wrapper(self, data: bytes):
        """
        Auto calling callback after processing data
        :param data: raw data
        :return: result of callback
        """
        return self._callback_after_parsing(self.parse(data))

    def serialize(self, data):
        return data.encode()

    @staticmethod
    def calculate_crc(data: bytes) -> int:
        """
        Calculating CRC16
        :param data: data for calculating CRC16
        :return: value of CRC16 (2 bytes)
        """
        crc = 0xFFFF
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(0, 8):
                crc = (crc << 1) ^ 0x1021 if (crc & 0x8000) else crc << 1
        return crc & 0xFFFF
