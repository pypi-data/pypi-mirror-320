import time
from typing import Callable, Any

from .auxiliary import *
from .models.data_parser import UsbDataParser
from .models.serial_model import SerialModel, STATUS_OK
from ..plugins import PyQtierPlugin


class UsbPluginManager(PyQtierPlugin):
    def __init__(self, with_baudrate: bool = False, default_baudrate: int = 9600):
        super().__init__()
        if with_baudrate:
            from .views.usb_control_with_baudrate import Ui_UsbWidget
        else:
            from .views.usb_control import Ui_UsbWidget

        self._with_baudrate: bool = with_baudrate
        if with_baudrate:
            self._default_baudrate: int = default_baudrate
        else:
            self._default_baudrate: int = 0
        self._ui = Ui_UsbWidget()
        self._serial: SerialModel = SerialModel()

        self._start_send_data_callback: Callable = lambda: ...
        self._stop_send_data_callback: Callable = lambda: ...

        self._obtain_data_callback: Callable = lambda: ...
        self._obtain_error_callback: Callable = lambda: ...

        # TODO: realize themes for plugin
        self.theme_settings: dict[str: Any[str, bool]] = THEME_SETTINGS

    def setup_view(self, *args, **kwargs):
        super().setup_view(*args, **kwargs)
        self._ui.cb_list_usb_devices.set_refresh_callback(self._cb_list_usb_devices_callback)
        self._cb_list_usb_devices_callback()

        if self._with_baudrate:
            self._ui.cb_list_baud_rates.addItems(BAUDRATES_LIST)
            self._ui.cb_list_baud_rates.setCurrentIndex(BAUDRATES_LIST.index(str(self._default_baudrate)))

        self.add_behaviours()

    def set_obtain_data_callback(self, callback: Callable):
        """
        Function which obtain data after obtaining and parsing
        :param callback: function
        :return: None
        """
        if callable(callback):
            self._serial.set_after_parsing_callback(callback)
            self._obtain_data_callback = self._serial.get_parse_callback()

            self._serial.data_received.connect(self._obtain_data_callback)
        else:
            raise TypeError("Callback must be callable")

    def set_obtain_error_callback(self, callback: Callable):
        if callable(callback):
            self._obtain_error_callback = callback
            self._serial.error_occurred.connect(self._obtain_error_callback)
        else:
            raise TypeError("Callback must be callable")

    def set_data_parser(self, data_parser: UsbDataParser):
        """
        Must be called before setting obtain data callback
        :param data_parser: class of DataParser
        :return: None
        """
        self._serial.set_data_parser(data_parser)

    def add_behaviours(self):
        self._ui.bt_connect_disconnect.clicked.connect(self._connect_disconnect_callback)

    def _connect_disconnect_callback(self):
        """

        """
        if self._serial.is_connected:
            self._stop_send_data_callback()
            # Не встигає відключитись від пристрою.
            time.sleep(0.01)

            self._serial.disconnect()

            # self.bt_com.setIcon(self.__icon_com_connect)
            self._ui.bt_connect_disconnect.setText("Connect")

            if self._statusbar:
                self._statusbar.showMessage(f"{self._ui.cb_list_usb_devices.currentText()} disconnected!", 4000)
        else:
            # Connecting
            self._serial.set_serial_port(self._ui.cb_list_usb_devices.currentText().split(" - ")[0])
            # Setting baud rate if it enabled
            if self._with_baudrate:
                self._serial.set_baud_rate(int(self._ui.cb_list_baud_rates.currentText()))

            # Checking if connecting successfully
            if self._serial.connect() == STATUS_OK:
                # self.bt_com.setIcon(self.__icon_com_disconnect)
                self._ui.bt_connect_disconnect.setText("Disconnect")
                if self._statusbar:
                    self._statusbar.showMessage(f"{self._ui.cb_list_usb_devices.currentText()} connected!", 4000)
                self._start_send_data_callback()
            else:
                if self._statusbar:
                    self._statusbar.showMessage(f"{self._ui.cb_list_usb_devices.currentText()} connection failure!",
                                                4000)
                # Updating list of device if connecting failure
                self._cb_list_usb_devices_callback()

    def _cb_list_usb_devices_callback(self):
        current_device = self._ui.cb_list_usb_devices.currentText()
        available_devices = self._serial.get_available_ports()
        self._ui.cb_list_usb_devices.clear()
        self._ui.cb_list_usb_devices.addItems(available_devices)
        if current_device in available_devices:
            self._ui.cb_list_usb_devices.setCurrentIndex(available_devices.index(current_device))

    def send(self, data: str) -> int:
        return self._serial.write(data)

    @staticmethod
    def help():
        print(HELP_TEXT)
