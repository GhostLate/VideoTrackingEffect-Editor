from PySide6 import QtGui
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QToolButton, QSlider


class OneStateButton(QToolButton):
    def __init__(self, object_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not object_name:
            self.setObjectName(object_name)
        self.clicked.connect(self.state_func)

    @Slot()
    def state_func(self):
        self.clicked_func()

    def set_clicked_func(self, func=None):
        self.clicked_func = func


class TwoStateButton(QToolButton):
    def __init__(self, clicked_icon: QIcon, unclicked_icon: QIcon, object_name: str=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not object_name:
            self.setObjectName(object_name)
        self.clicked.connect(self.state_func)
        self.is_clicked = False
        self.clicked_icon = clicked_icon
        self.unclicked_icon = unclicked_icon
        self.setIcon(self.clicked_icon)

    @Slot()
    def state_func(self):
        self.is_clicked = not self.is_clicked
        if self.is_clicked:
            self.setIcon(self.unclicked_icon)
            self.clicked_func()
        else:
            self.setIcon(self.clicked_icon)
            self.unclicked_func()

    def set_unclicked_func(self, func=None):
        self.unclicked_func = func

    def set_clicked_func(self, func=None):
        self.clicked_func = func

    def switch_state(self):
        self.is_clicked = not self.is_clicked
        self.setIcon(self.unclicked_icon) if self.is_clicked else self.setIcon(self.clicked_icon)


class CustomSlider(QSlider):
    def __init__(self, object_name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not object_name:
            self.setObjectName(object_name)
        self.valueChanged.connect(self.state_func)
        self.isPressed = False

    @Slot()
    def state_func(self):
        self.value_changed_func()

    def set_value_changed_func(self, func=None):
        self.value_changed_func = func

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super(CustomSlider, self).mousePressEvent(event)
        self.isPressed = True

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super(CustomSlider, self).mousePressEvent(event)
        self.isPressed = False


class CustomAction(QAction):
    def __init__(self, object_name: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not object_name:
            self.setObjectName(object_name)
        self.triggered.connect(self.trigger)

    @Slot()
    def trigger(self):
        self.trigger_func()

    def set_trigger_func(self, func=None):
        self.trigger_func = func