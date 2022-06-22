import sys

from PySide6.QtCore import QStandardPaths
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
from qt_material import apply_stylesheet

from ui.main_window import UIMainWindow
from utils.audio_output import AudioOutput
from utils.media_player import MediaPlayer
from utils.media_utils import save_media, MediaFormat


class PlayerWindow(UIMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = MediaPlayer(self)
        self.audio_output = AudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)

        self.control_panel.volumeSlider.setValue(self.audio_output.volume() * 100)
        self.switch_control_state()

        @self.menu_panel.actionOpen.set_trigger_func
        def onOpenVideo():
            self.media_player.ensure_stopped()
            file_dialog = QFileDialog(self)
            file_dialog.setOptions(QFileDialog.DontUseNativeDialog)

            if not self.media_player.media_format.mime_types:
                self.media_player.media_format.update_mini_types()

            file_dialog.setMimeTypeFilters(self.media_player.media_format.mime_types)

            default_mimetype = MediaFormat.AVI if self.media_player.media_format.is_windows else MediaFormat.MP4
            if default_mimetype in self.media_player.media_format.mime_types:
                file_dialog.selectMimeTypeFilter(default_mimetype)

            movies_location = QStandardPaths.writableLocation(QStandardPaths.MoviesLocation)
            file_dialog.setDirectory(movies_location)

            if file_dialog.exec() == QDialog.Accepted:
                self.media_player.setSource(file_dialog.selectedUrls()[0])

        @self.menu_panel.actionSave.set_trigger_func
        def onSaveVideo():
            if self.media_player.source().path():
                result = save_media(self.media_player.source().path(),
                                    self.media_player.source().path().replace(".mp4", "_modded.mp4"),
                                    self.media_player.mod_frame_rect,
                                    (self.media_player.meta_data.width // 2, self.media_player.meta_data.height // 2))
                if result:
                    self.show_status_message("Saved successfully.")
                else:
                    self.show_status_message("Wrong Frame resolution while saving.")
            else:
                print(False)

        @self.menu_panel.actionSave_As.set_trigger_func
        def onSaveAsVideo():
            #onSaveVideo()
            import pandas as pd
            import numpy as np
            arr = np.array(self.media_player.mod_frame_rect)
            dict = {
                'x1': arr[:, 0, 0],
                'y1': arr[:, 0, 1],
                'x2': arr[:, 1, 0],
                'y2': arr[:, 1, 1]
            }
            df = pd.DataFrame(dict)
            df.to_csv('data.csv')
            print("Data saved")

        @self.menu_panel.actionAbout.set_trigger_func
        def onAboutApp():
            print("About")

    def closeEvent(self, event):
        self.media_player.ensure_stopped()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = PlayerWindow()
    apply_stylesheet(app, theme='light_cyan_500.xml')
    main_win.show()
    sys.exit(app.exec())
