"""
 Python wrapper for libui.

"""

from .callback_helper import get_c_callback_func_ptr, c_func_type_void_structp_voidp
from pylibui import libui
from .control import Control


class BaseEntry(Control):

    def setText(self, text):
        """
        Sets the text of the entry.

        :param text: string
        :return: None
        """
        libui.uiEntrySetText(self.control, text)

    def getText(self):
        """
        Returns the text of the entry.

        :return: string
        """
        return libui.uiEntryText(self.control)

    def setReadOnly(self, read_only):
        """
        Sets whether the entry is read only or not.

        :param read_only: bool
        :return: None
        """
        libui.uiEntrySetReadOnly(self.control, int(read_only))

    def getReadOnly(self):
        """
        Returns whether the entry is read only or not.

        :return: bool
        """
        return bool(libui.uiEntryReadOnly(self.control))

    def onChanged(self, data):
        """
        Executes when the entry is changed.

        :param data: data
        :return: None
        """
        pass


class Entry(BaseEntry):

    def __init__(self):
        """
        Creates a new entry.

        """
        super().__init__()
        self.control = self._create_control()

        def handler(window, data):
            self.onChanged(data)
            return 0

        self._change_callback_ptr, self._change_callback = \
          get_c_callback_func_ptr(handler, c_func_type_void_structp_voidp)
        self.changedHandler = libui.uiEntryOnChanged(self.control,
                                                    self._change_callback_ptr,
                                                     None)

    def _create_control(self):
        return libui.uiNewEntry()

class PasswordEntry(Entry):

    def _create_control(self):
        return libui.uiNewPasswordEntry()


class SearchEntry(Entry):

    def _create_control(self):
        return libui.uiNewSearchEntry()
