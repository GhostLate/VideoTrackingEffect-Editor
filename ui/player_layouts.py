from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QHBoxLayout,
                               QLabel, QMenu,
                               QMenuBar, QSizePolicy, QSpacerItem)

from ui.player_widgets import PlayPauseBotton, SettingsButton, BackButton, NextButton, \
    VolumeButton, VolumeSlider, TimeSlider, Next10Button, Back10Button
from utils.custom_widgets import CustomAction


class ControlPanel:
    def __init__(self, icons, parent=None):
        self.playButton = PlayPauseBotton(parent=parent,
                                          clicked_icon=icons.play_icon,
                                          unclicked_icon=icons.pause_icon,
                                          object_name=u"playButton")

        self.volumeButton = VolumeButton(parent=parent,
                                         clicked_icon=icons.speaker_on_icon,
                                         unclicked_icon=icons.speaker_off_icon,
                                         object_name=u"volumeButton")

        self.settingsButton = SettingsButton(parent=parent,
                                             icon=icons.equalizer_icon,
                                             object_name=u"settingsButton")

        self.backButton = BackButton(parent=parent,
                                     icon=icons.back_icon,
                                     object_name=u"previousButton")

        self.nextButton = NextButton(parent=parent,
                                     icon=icons.next_icon,
                                     object_name=u"nextButton")

        self.back10Button = Back10Button(parent=parent,
                                         icon=icons.back_10_icon,
                                         object_name=u"previous10Button")

        self.next10Button = Next10Button(parent=parent,
                                         icon=icons.next_10_icon,
                                         object_name=u"next10Button")

        self.volumeSlider = VolumeSlider(parent=parent,
                                         object_name=u"nextButton")

        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer = QLabel()
        spacer.setFixedWidth(100)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setObjectName(u"controlLayout")
        self.layout.setContentsMargins(10, -1, 10, -1)

        self.layout.addWidget(self.settingsButton)
        self.layout.addWidget(spacer)
        self.layout.addItem(horizontalSpacer)
        self.layout.addWidget(self.back10Button)
        self.layout.addWidget(self.backButton)
        self.layout.addWidget(self.playButton)
        self.layout.addWidget(self.nextButton)
        self.layout.addWidget(self.next10Button)
        self.layout.addItem(horizontalSpacer)
        self.layout.addWidget(self.volumeButton)
        self.layout.addWidget(self.volumeSlider)

    def switch_state(self):
        self.settingsButton.setEnabled(not self.settingsButton.isEnabled())
        self.back10Button.setEnabled(not self.back10Button.isEnabled())
        self.backButton.setEnabled(not self.backButton.isEnabled())
        self.playButton.setEnabled(not self.playButton.isEnabled())
        self.nextButton.setEnabled(not self.nextButton.isEnabled())
        self.next10Button.setEnabled(not self.next10Button.isEnabled())
        self.volumeButton.setEnabled(not self.volumeButton.isEnabled())
        self.volumeSlider.setEnabled(not self.volumeSlider.isEnabled())


class TimePanel:
    def __init__(self, parent=None):
        self.timeSlider = TimeSlider(parent=parent,
                                     object_name=u"timeSlider")

        self.currentTimeLabel = QLabel(parent=parent,
                                       text=u"00:00:00.000")
        self.currentTimeLabel.setObjectName(u"currentTimeLabel")

        self.totalTimeLabel = QLabel(parent=parent,
                                     text=u"00:00:00.000")
        self.totalTimeLabel.setObjectName(u"totalTimeLabel")

        self.layout = QHBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setObjectName(u"timeLayout")
        self.layout.setContentsMargins(10, -1, 10, 0)

        self.layout.addWidget(self.currentTimeLabel)
        self.layout.addWidget(self.timeSlider)
        self.layout.addWidget(self.totalTimeLabel)

    def switch_state(self):
        self.timeSlider.setEnabled(not self.timeSlider.isEnabled())


class VideoPanel:
    def __init__(self, parent=None):
        self.layout = QHBoxLayout()
        self.layout.setSpacing(1)
        self.layout.setObjectName(u"videolLayout")

        self.videoWidget_1 = QVideoWidget(parent=parent)
        self.videoWidget_1.setObjectName(u"wigglyWidget_2")

        self.videoWidget_2 = QVideoWidget(parent=parent)
        self.videoWidget_2.setObjectName(u"wigglyWidget")

        videoWidget_sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.videoWidget_1.setSizePolicy(videoWidget_sizePolicy)
        self.videoWidget_2.setSizePolicy(videoWidget_sizePolicy)

        self.layout.addWidget(self.videoWidget_1)
        self.layout.addWidget(self.videoWidget_2)


class MenuPanel:
    def __init__(self, MainWindow):
        self.actionOpen = CustomAction(parent=MainWindow, text=u"Open", object_name=u"actionOpen")
        self.actionSave = CustomAction(parent=MainWindow, text=u"Save", object_name=u"actionSave")
        self.actionSave_As = CustomAction(parent=MainWindow, text=u"Save As", object_name=u"actionSaveAs")
        self.actionAbout = CustomAction(parent=MainWindow, text=u"About", object_name=u"actionAbout")

        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")

        self.menuFile = QMenu(self.menubar, title=u"File")
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.actionAbout)
