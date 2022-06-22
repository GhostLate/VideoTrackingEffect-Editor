from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon


class Icons:
    def __init__(self, dark_theme=False):
        self.equalizer_icon = QIcon()
        self.equalizer_icon.addFile(u"icons/equalizer.png", QSize(), QIcon.Normal, QIcon.Off)
        self.play_icon = QIcon()
        self.play_icon.addFile(u"icons/play-button.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pause_icon = QIcon()
        self.pause_icon.addFile(u"icons/pause.png", QSize(), QIcon.Normal, QIcon.Off)
        self.stop_icon = QIcon()
        self.stop_icon.addFile(u"icons/stop.png", QSize(), QIcon.Normal, QIcon.Off)
        self.back_icon = QIcon()
        self.back_icon.addFile(u"icons/back.png", QSize(), QIcon.Normal, QIcon.Off)
        self.next_icon = QIcon()
        self.next_icon.addFile(u"icons/next.png", QSize(), QIcon.Normal, QIcon.Off)
        self.back_10_icon = QIcon()
        self.back_10_icon.addFile(u"icons/back_10.png", QSize(), QIcon.Normal, QIcon.Off)
        self.next_10_icon = QIcon()
        self.next_10_icon.addFile(u"icons/next_10.png", QSize(), QIcon.Normal, QIcon.Off)
        self.speaker_off_icon = QIcon()
        self.speaker_off_icon.addFile(u"icons/speaker_off.png", QSize(), QIcon.Normal, QIcon.Off)
        self.speaker_on_icon = QIcon()
        self.speaker_on_icon.addFile(u"icons/speaker_on.png", QSize(), QIcon.Normal, QIcon.Off)
        self.replay_icon = QIcon()
        self.replay_icon.addFile(u"icons/replay.png", QSize(), QIcon.Normal, QIcon.Off)