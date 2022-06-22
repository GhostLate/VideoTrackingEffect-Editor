from PySide6.QtCore import Slot
from PySide6.QtMultimedia import QAudioOutput

from ui.main_window import UIMainWindow


class AudioOutput(QAudioOutput):
    player_window: UIMainWindow

    def __init__(self, player_window: UIMainWindow):
        super().__init__()
        self.player_window = player_window
        self.volumeChanged.connect(self.onVolumeChange)

        @self.player_window.control_panel.volumeSlider.set_value_changed_func
        def onSliderPositionChange():
            self.setVolume(self.player_window.control_panel.volumeSlider.value() / 100)
            if self.player_window.control_panel.volumeSlider.value() == 0 and not self.player_window.control_panel.volumeButton.is_clicked:
                self.player_window.control_panel.volumeButton.switch_state()
            if self.player_window.control_panel.volumeSlider.value() > 0 and self.player_window.control_panel.volumeButton.is_clicked:
                self.player_window.control_panel.volumeButton.switch_state()

        @self.player_window.control_panel.volumeButton.set_clicked_func
        def onVolumeOff():
            self.player_window.control_panel.volumeSlider.setValue(0)

        @self.player_window.control_panel.volumeButton.set_unclicked_func
        def onVolumeOn():
            self.player_window.control_panel.volumeSlider.setValue(100)

    @Slot()
    def onVolumeChange(self):
        self.player_window.control_panel.volumeSlider.setValue(self.volume() * 100)
