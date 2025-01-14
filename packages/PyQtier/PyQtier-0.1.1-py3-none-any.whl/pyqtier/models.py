# -*- coding: utf-8 -*-
from configparser import ConfigParser

from . import auxiliary


class PyQtierSettingsModel(object):
    _config = ConfigParser()

    def __init__(self, settings_id: str = "main"):
        self._defaults = auxiliary.CONFIG_DEFAULTS
        self._config.read(auxiliary.CONFIG_FILE_PATH)

        # Sections
        self.__ui = None

        self._settings_id = settings_id

        self.load_configs()

    def load_configs(self) -> None:
        """
        Load configuration from file
        :return: None
        """
        try:
            for section in auxiliary.CONFIG_SECTIONS:
                if section not in self._config.sections():
                    self._config.add_section(section)
            self.__ui = self._config["UI"]
        except KeyError as err:
            raise KeyError(f"Key '{err}' does not exist in config file")

    def update_config_file(self) -> None:
        """
        Update configuration or create new config file
        :return: None
        """
        with open(auxiliary.CONFIG_FILE_PATH, 'w') as configfile:
            self._config.write(configfile)

    def get_default(self, key: str, if_none: str = ""):
        if key in self._defaults:
            return self._defaults[key]
        return if_none

    @property
    def settings_id_for_config(self) -> str:
        return self._settings_id + "_" if self._settings_id else ""

    @property
    def settings_id(self) -> str:
        return self._settings_id

    @property
    def window_size(self) -> tuple:
        """
        :return: tuple (width, height)
        """
        return tuple(map(int, self.__ui.get(
            self.settings_id_for_config + "window_size",
            fallback=self.get_default(self.settings_id_for_config + "window_size", if_none="0x0")
        ).split('x')))

    @property
    def window_position(self) -> tuple:
        """
        :return: tuple (x, y)
        """

        return tuple(map(int, self.__ui.get(
            self.settings_id_for_config + "window_position",
            fallback=self.get_default(self.settings_id_for_config + "window_position", if_none="0,0")
        ).split(",")))

    @property
    def is_maximized(self) -> bool:
        return self.__ui.getboolean(self.settings_id_for_config + "is_maximized", fallback=False)

    def set_window_size(self, width, height) -> None:
        """
        Saving main window size parameters
        :param width: width of main window (px)
        :param height: height of main window (px)
        :return: None
        """
        self._config.set("UI", self.settings_id_for_config + "window_size", f"{width}x{height}")
        self.update_config_file()

    def set_window_position(self, x: int, y: int) -> None:
        """
        Saving main window position parameters
        :param x: x position of main window (px)
        :param y: y position of main window (px)
        :param is_maximized: is window showing full screen (True)
        :return: None
        """
        self._config.set("UI", self.settings_id_for_config + "window_position", f"{x},{y}")
        self.update_config_file()

    def set_maximized(self, is_maximized: bool = False) -> None:
        """
        Saving state of main window position parameters
        :param is_maximized: is window showing full screen (True)
        :return: None
        """
        self._config.set("UI", self.settings_id_for_config + "is_maximized", f"{is_maximized}")
        self.update_config_file()
