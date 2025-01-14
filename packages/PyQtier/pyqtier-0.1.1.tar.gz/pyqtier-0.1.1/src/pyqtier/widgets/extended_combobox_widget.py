from typing import Callable

from PyQt5 import QtCore, QtWidgets


class ExtendedComboBox(QtWidgets.QComboBox):
    """
    ComboBox з автооновленням списку даних.
    Для оновлення потрібно встановити callback
    використовуючи метод set_refresh_callback(<callback>).
    При натисканні на ComboBox список даних в ньому
    перед відкриттям буде оновлюватись.
    """

    popupAboutToBeShown = QtCore.pyqtSignal()

    def __init__(self, *args):
        super(ExtendedComboBox, self).__init__(*args)
        self.__refresh_callback = None

    def set_refresh_callback(self, update_callback: Callable):
        """
        Встановити Callback оновлення списку елементів, який у випадку відкривання
        ComboBox буде викликатись перед показом елементів.
        :param update_callback: Функція-callback, що виконуватиме оновлення даних в ComboBox
        :return: None
        """
        if callable(update_callback):
            self.__refresh_callback = update_callback

    def showPopup(self):
        """
        Метод, що промальовує елементи при відкриванні ComboBox.
        Перед викликом основного метода викликається RefreshCallback
        :return: None
        """
        if self.__refresh_callback:
            self.__refresh_callback()
        self.popupAboutToBeShown.emit()
        super(ExtendedComboBox, self).showPopup()
