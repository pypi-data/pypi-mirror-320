from typing import Callable, Optional

import serial
from PyQt5.QtCore import QThread, pyqtSignal
from serial.tools import list_ports

from .data_parser import UsbDataParser
from .statuses import *


class SerialModel(QThread):
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._baud_rate = 0
        self._is_connection_via_usb = False
        self._serial_port = "COM1"
        self._ser = None
        self._is_serial_connected = False
        self._com_connection_lost_callback = None
        self._data_parser: Optional[UsbDataParser] = None

    def set_connection_type(self, is_connection_via_usb: bool):
        self._is_connection_via_usb = is_connection_via_usb

    def set_com_connection_lost_callback(self, callback: Callable):
        if callable(callback):
            self._com_connection_lost_callback = callback
            return STATUS_OK
        return STATUS_OBJECT_NOT_CALLABLE

    def set_serial_port(self, serial_port: str) -> int:
        """
        Setter of Serial port.
        :param serial_port: str name of Serial ports
        :return: 0 if everything is OK,
                 1 if not (FAILED)
        """
        if isinstance(serial_port, str):
            self._serial_port = serial_port
            return STATUS_OK
        return STATUS_ERROR

    def set_baud_rate(self, br: int = 115200) -> int:
        """
        Method for setting baud rate
        :param br: can be 9600 - 115200 (default value)
        :return: 0 if everything is OK,
                 1 if not (FAILED)
        """
        if isinstance(br, int):
            self._baud_rate = br
            return STATUS_OK
        return STATUS_ERROR

    def set_data_parser(self, data_parser: UsbDataParser):
        if isinstance(data_parser, UsbDataParser):
            self._data_parser = data_parser
        else:
            raise TypeError("Argument must be a DataParser object")

    def set_after_parsing_callback(self, callback: Callable):
        self._data_parser.set_callback_after_parsing(callback)

    def get_parse_callback(self) -> Callable:
        return self._data_parser.parse_wrapper

    @property
    def is_connected(self) -> bool:
        return self._is_serial_connected

    def connect(self) -> int:
        """
        Method which is connecting to Serial device.
        :return: 0 if everything is OK,
                 1 if SerialException (FAILED)
        """
        try:
            self._ser = serial.Serial(self._serial_port, self._baud_rate)
            self.start()
        except serial.SerialException:
            return STATUS_ERROR
        else:
            self._is_serial_connected = True
            return STATUS_OK

    def disconnect(self) -> int:
        """
        Method which is disconnecting from Serial device.
        :return: 0 if everything is OK,
                 1 if SerialException (FAILED)
        """
        try:
            self._is_serial_connected = False
            self.wait()
            self._ser.close()
        except serial.SerialException:
            return STATUS_ERROR
        except AttributeError:
            return STATUS_ERROR
        else:
            return STATUS_OK

    def write(self, data) -> int:
        """
        Write data to serial port
        :param data:
        :return: Кількість надісланих байт
        """
        if self._is_serial_connected:
            try:
                if self._data_parser is not None:
                    serialized_data = self._data_parser.serialize(data)
                    return self._ser.write(serialized_data)
                else:
                    return 0
            except serial.serialutil.SerialTimeoutException:
                # Якщо COM-порту не знайдено - розриваємо зв'язок
                self.disconnect()
                self._com_connection_lost_callback()
                return STATUS_ERROR_CONNECTION_TIMEOUT

    def run(self):
        try:
            while self.is_connected:
                if self._ser.in_waiting:
                    data = self._ser.read(self._ser.in_waiting)
                    self.data_received.emit(data)
                self.msleep(10)  # small delay for decrease load
        except Exception as e:
            self.error_occurred.emit(str(e))

    @staticmethod
    def get_available_ports(item_as_str: bool = True) -> list[str]:
        """
        Get available on system serial ports
        :param item_as_str: True if you need str name of serial ports, False if you need ListPortInfo
        :return: List of available serial ports
        """
        return [str(i) for i in list_ports.comports()] if item_as_str else list_ports.comports()
