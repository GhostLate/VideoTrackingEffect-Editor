import sys

import cv2
import numpy as np
from PySide6.QtCore import Slot
from PySide6.QtMultimedia import QMediaPlayer, QVideoFrame, QVideoSink
from utils.media_utils import MediaFormat, ms_to_hours, MetaData
from utils.object_tracking import ObjectTracker
from utils.video_handler import FrameProvider, q_image2numpy

from ui.main_window import UIMainWindow
from ui.player_widgets import PlayerResizableRect


class MediaPlayer(QMediaPlayer):
    media_format: MediaFormat
    meta_data: MetaData
    mod_frame_rect: np.array
    frames_time: list
    resizable_band: PlayerResizableRect
    tracker: ObjectTracker

    def __init__(self, player_window: UIMainWindow):
        super().__init__()
        self.player_window = player_window
        self.media_format = MediaFormat()

        self.errorOccurred.connect(self.player_error)
        self.positionChanged.connect(self.onMediaPositionChange)
        self.durationChanged.connect(self.onMediaDurationChange)
        self.playbackStateChanged.connect(self.onPlaybackStateChange)
        self.mediaStatusChanged.connect(self.onMediaStatusChanged)

        self.frame_provider_default = FrameProvider()
        self.frame_provider_default.video_sink = self.player_window.video_panel.videoWidget_1.videoSink()

        self.frame_provider_modified = FrameProvider()
        self.frame_provider_modified.video_sink = self.player_window.video_panel.videoWidget_2.videoSink()

        self.track = True
        self.last_frame_idx = 0
        self.curr_frame_idx = 0
        self.curr_frame_timestamp = 0
        self.curr_frame = np.array([])

        def handle_video_frame_changed(video_frame: QVideoFrame):
            self.curr_frame_timestamp = round(video_frame.startTime() / 1000)
            self.curr_frame_idx = self.position2frame_id(self.curr_frame_timestamp)

            image = video_frame.toImage()
            np_array = q_image2numpy(image)

            self.frame_provider_default.write_frame(np_array)

            if (self.resizable_band.resizing or self.resizable_band.moving) and self.curr_frame_idx > 0:
                self.mod_frame_rect[self.curr_frame_idx] = self.mod_frame_rect[self.curr_frame_idx - 1]
            elif self.curr_frame_idx > 0 and self.last_frame_idx < self.curr_frame_idx:
                bbox_exist, bbox = self.tracker.update_frame(np_array)
                if not bbox_exist:
                    self.tracker.update_roi(self.curr_frame, self.mod_frame_rect[self.curr_frame_idx - 1])
                    bbox_exist, bbox = self.tracker.update_frame(np_array)
                self.mod_frame_rect[self.curr_frame_idx] = bbox
            elif self.curr_frame_idx == 0:
                self.tracker.update_roi(np_array, self.mod_frame_rect[0])
            else:
                self.tracker.update_roi(self.curr_frame, self.mod_frame_rect[self.curr_frame_idx])

            self.curr_frame = np_array.copy()
            self.resizable_band.set_cords(self.mod_frame_rect[self.curr_frame_idx])

            cv2.rectangle(np_array,
                          self.mod_frame_rect[self.curr_frame_idx, 0],
                          self.mod_frame_rect[self.curr_frame_idx, 1],
                          (255, 255, 255), 3)
            self.frame_provider_modified.write_frame(np_array)

            self.last_frame_idx = self.curr_frame_idx

        self.setVideoSink(QVideoSink(self))
        self.videoSink().videoFrameChanged.connect(handle_video_frame_changed)

        @self.player_window.control_panel.playButton.set_clicked_func
        def onPlayMedia():
            self.play()

        @self.player_window.control_panel.playButton.set_unclicked_func
        def onPauseMedia():
            self.pause()

        @self.player_window.control_panel.backButton.set_clicked_func
        def onBackMedia():
            if self.curr_frame_idx - 1 >= 0:
                self.curr_frame_idx -= 1
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.curr_frame_timestamp)

        @self.player_window.control_panel.back10Button.set_clicked_func
        def onBack10Media():
            if self.curr_frame_idx - 10 >= 0:
                self.curr_frame_idx -= 10
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.curr_frame_timestamp)
            else:
                self.curr_frame_idx = 0
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.curr_frame_timestamp)

        @self.player_window.control_panel.nextButton.set_clicked_func
        def onNextMedia():
            if self.curr_frame_idx + 1 < self.meta_data.nb_frames:
                self.curr_frame_idx += 1
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.curr_frame_timestamp)

        @self.player_window.control_panel.next10Button.set_clicked_func
        def onNext10Media():
            if self.curr_frame_idx + 10 < self.meta_data.nb_frames:
                self.curr_frame_idx += 10
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.curr_frame_timestamp)
            else:
                self.curr_frame_idx = self.meta_data.nb_frames - 1
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.duration())

        @self.player_window.time_panel.timeSlider.set_value_changed_func
        def onSliderPositionChanged():
            if self.player_window.time_panel.timeSlider.isPressed:
                self.curr_frame_idx = int(self.player_window.time_panel.timeSlider.value())
                self.curr_frame_timestamp = self.frame_id2position(self.curr_frame_idx)
                self.setPosition(self.curr_frame_timestamp)

    def setSource(self, source):
        self.meta_data = MetaData(source)
        self.mod_frame_rect = np.zeros(shape=(round(self.meta_data.nb_frames * 1.01), 2, 2), dtype=int)
        self.mod_frame_rect[:, 0, :] = np.round(np.array([self.meta_data.width, self.meta_data.height]) / 4).astype(int)
        self.mod_frame_rect[:, 1, :] = np.round(np.array([self.meta_data.width, self.meta_data.height]) / 4 * 3).astype(int)
        super().setSource(source)
        self.resizable_band = PlayerResizableRect(frame_res=[self.meta_data.width, self.meta_data.height],
                                                  parent=self.player_window.video_panel.videoWidget_2)
        self.tracker = ObjectTracker(res_rate=2)

        self.play()
        self.pause()

        @self.resizable_band.set_frame_update_func
        def onFrameUpdate():
            self.mod_frame_rect[self.curr_frame_idx] = self.resizable_band.get_cords()
            np_array = self.curr_frame.copy()
            cv2.rectangle(np_array,
                          self.mod_frame_rect[self.curr_frame_idx, 0],
                          self.mod_frame_rect[self.curr_frame_idx, 1],
                          (255, 255, 255), 3)
            self.frame_provider_modified.write_frame(np_array)

        @self.resizable_band.set_data_update_func
        def onDataUpdate():
            self.tracker.update_roi(self.curr_frame, self.mod_frame_rect[self.curr_frame_idx])

    def frame_id2position(self, frame_id: int) -> int:
        return self.meta_data.timestamps[frame_id]

    def position2frame_id(self, position: int) -> int:
        return self.meta_data.timestamp2frame_id(position)

    @Slot()
    def onMediaPositionChange(self):
        if self.curr_frame_idx < self.meta_data.nb_frames:
            self.player_window.time_panel.timeSlider.setValue(self.position2frame_id(self.curr_frame_timestamp))
            self.player_window.time_panel.currentTimeLabel.setText(ms_to_hours(self.curr_frame_timestamp))
        else:
            self.stop()

    @Slot()
    def onMediaDurationChange(self):
        self.player_window.time_panel.timeSlider.setRange(0, self.meta_data.nb_frames - 1)
        self.player_window.time_panel.totalTimeLabel.setText(ms_to_hours(self.duration()))

    @Slot()
    def onPlaybackStateChange(self, state: QMediaPlayer.PlaybackState):
        if state == (QMediaPlayer.PausedState or QMediaPlayer.StoppedState):
            if self.player_window.control_panel.playButton.is_clicked:
                self.player_window.control_panel.playButton.switch_state()
        elif state == QMediaPlayer.PlayingState:
            if not self.player_window.control_panel.playButton.is_clicked:
                self.player_window.control_panel.playButton.switch_state()
        if state == QMediaPlayer.StoppedState:
            self.player_window.control_panel.playButton.setIcon(self.player_window.icons.replay_icon)

    @Slot()
    def onMediaStatusChanged(self, state: QMediaPlayer.MediaStatus):
        if state == QMediaPlayer.MediaStatus.LoadedMedia:
            if not self.player_window.time_panel.timeSlider.isEnabled():
                self.player_window.switch_control_state()
        elif state == QMediaPlayer.MediaStatus.NoMedia:
            if self.player_window.time_panel.timeSlider.isEnabled():
                self.player_window.switch_control_state()

    @Slot(QMediaPlayer.Error, str)
    def player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.player_window.show_status_message(error_string)

    @Slot()
    def ensure_stopped(self):
        if self.playbackState() != QMediaPlayer.StoppedState:
            self.stop()

