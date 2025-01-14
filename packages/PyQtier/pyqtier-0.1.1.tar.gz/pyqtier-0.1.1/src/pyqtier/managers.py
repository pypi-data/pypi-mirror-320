# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets

from .registry import PyQtierWindowsRegistry


class PyQtierWindowsManager:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window_widget = QtWidgets.QMainWindow()
        self.main_window = None

        self.widget_registry = PyQtierWindowsRegistry()
        self.widget_registry.create_registered_widgets()

        self.setup_manager()

    def setup_manager(self):
        ...

    def setup_main_window(self, ui, main_window_view, settings):
        """
        Setup main
        """
        self.main_window = main_window_view()
        self.main_window.setup_view(ui=ui, settings=settings, widget=self.main_window_widget, settings_id="main")

    def show_ui(self):
        self.main_window.open()
        sys.exit(self.app.exec_())
