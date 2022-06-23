from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon


class Icons:
    def __init__(self, config):
        if config['SETTINGS']['dark_mod']:
            mod = 'WHITE'
        else:
            mod = 'DARK'
        icon_paths = config['ICONS']

        self.equalizer_icon = QIcon()
        self.equalizer_icon.addFile(icon_paths[mod]['equalizer_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.play_icon = QIcon()
        self.play_icon.addFile(icon_paths[mod]['play_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.pause_icon = QIcon()
        self.pause_icon.addFile(icon_paths[mod]['pause_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.stop_icon = QIcon()
        self.stop_icon.addFile(icon_paths[mod]['stop_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.back_icon = QIcon()
        self.back_icon.addFile(icon_paths[mod]['back_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.next_icon = QIcon()
        self.next_icon.addFile(icon_paths[mod]['next_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.back_10_icon = QIcon()
        self.back_10_icon.addFile(icon_paths[mod]['back_10_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.next_10_icon = QIcon()
        self.next_10_icon.addFile(icon_paths[mod]['next_10_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.speaker_off_icon = QIcon()
        self.speaker_off_icon.addFile(icon_paths[mod]['speaker_off_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.speaker_on_icon = QIcon()
        self.speaker_on_icon.addFile(icon_paths[mod]['speaker_on_icon'], QSize(), QIcon.Normal, QIcon.Off)
        self.replay_icon = QIcon()
        self.replay_icon.addFile(icon_paths[mod]['replay_icon'], QSize(), QIcon.Normal, QIcon.Off)
