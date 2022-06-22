from PySide6.QtWidgets import (QMainWindow, QStatusBar, QVBoxLayout,
                               QWidget)
from resources import Icons
from ui.player_layouts import ControlPanel, TimePanel, VideoPanel, MenuPanel


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName(u"centralWidget")

        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName(u"statusbar")

        self.icons = Icons()

        self.menu_panel = MenuPanel(self)
        self.video_panel = VideoPanel(self)
        self.time_panel = TimePanel(self)
        self.control_panel = ControlPanel(self.icons, self)

        self.setObjectName(u"mainWindow")
        self.setWindowTitle(u"Player")
        self.resize(self.screen().availableGeometry().width() / 2, self.screen().availableGeometry().height() / 2)

        self.setCentralWidget(self.centralWidget)
        self.setMenuBar(self.menu_panel.menubar)
        self.setStatusBar(self.statusbar)

        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainLayout.setSpacing(5)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addLayout(self.video_panel.layout)
        self.mainLayout.addLayout(self.time_panel.layout)
        self.mainLayout.addLayout(self.control_panel.layout)

    def switch_control_state(self):
        self.control_panel.switch_state()
        self.time_panel.switch_state()

    def show_status_message(self, message):
        self.statusBar().showMessage(message, 5000)
