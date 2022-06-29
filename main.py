import sys

import cv2
from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog
import qt_material

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

        self.media_player.setSource(QUrl("/home/ghost/Desktop/VideoTrackingEffect-Editor/data/sample.mp4"))

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
            # onSaveVideo()
            import pandas as pd
            rect_dict = {
                'x1': self.media_player.mod_frame_rect[:, 0, 0],
                'y1': self.media_player.mod_frame_rect[:, 0, 1],
                'x2': self.media_player.mod_frame_rect[:, 1, 0],
                'y2': self.media_player.mod_frame_rect[:, 1, 1]
            }
            df = pd.DataFrame(rect_dict)
            df.to_csv('data/data.csv')
            print("Data saved")

        @self.menu_panel.actionAbout.set_trigger_func
        def onAboutApp():
            print("About")

    def closeEvent(self, event):
        self.media_player.ensure_stopped()
        event.accept()

    def resizeEvent(self, event):
        if self.media_player.mediaStatus() == QMediaPlayer.MediaStatus.LoadedMedia:
            self.media_player.resizable_band.set_cords(self.media_player.mod_frame_rect[self.media_player.curr_frame_idx])
            self.media_player.mod_frame_rect[self.media_player.curr_frame_idx] = self.media_player.resizable_band.get_cords()
            np_array = self.media_player.curr_frame.copy()
            cv2.rectangle(np_array,
                          self.media_player.mod_frame_rect[self.media_player.curr_frame_idx, 0],
                          self.media_player.mod_frame_rect[self.media_player.curr_frame_idx, 1],
                          (255, 255, 255), 3)
            self.media_player.frame_provider_modified.write_frame(np_array)
        return super().resizeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = PlayerWindow()
    if main_win.config['SETTINGS']['dark_mod']:
        qt_material.apply_stylesheet(app, theme=main_win.config['SETTINGS']['dark_mod_theme'])
    else:
        qt_material.apply_stylesheet(app, theme=main_win.config['SETTINGS']['white_mod_theme'])
    main_win.show()
    sys.exit(app.exec())
