import numpy as np
from PySide6.QtCore import Qt, Slot, QSize, QPoint

from utils.custom_widgets import TwoStateButton, OneStateButton, CustomSlider
from utils.resizable_rect import ResizableRect


class PlayPauseButton(TwoStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VolumeButton(TwoStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StopButton(OneStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SettingsButton(OneStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BackButton(OneStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NextButton(OneStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Back10Button(OneStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Next10Button(OneStateButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VolumeSlider(CustomSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Horizontal)
        self.setMinimumWidth(100)
        self.setMaximumWidth(100)
        self.setRange(0, 100)

    @Slot()
    def state_func(self):
        self.value_changed_func()

    def set_value_changed_func(self, func=None):
        self.value_changed_func = func


class TimeSlider(CustomSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOrientation(Qt.Horizontal)

    @Slot()
    def state_func(self):
        self.value_changed_func()

    def set_value_changed_func(self, func=None):
        self.value_changed_func = func


class PlayerResizableRect(ResizableRect):
    def __init__(self, parent, frame_res: [int, int]):
        super().__init__(parent)
        self.frame_res = np.array(frame_res)
        pix_window_res = np.array(self.parent.size().toTuple())
        window_res = self.pix2window_res(pix_window_res)
        frame_cords = np.round([self.frame_res / 4, self.frame_res / 4 * 3]).astype(int)
        window_cords = self.frame_cords2window_cords(frame_cords, window_res)
        self.set_cords(window_cords)

    def frame_res2pix(self, frame_res, pix_window_res) -> np.array:
        if frame_res[0] / frame_res[1] > 1:
            b = pix_window_res[0] / frame_res[0]
        else:
            b = pix_window_res[1] / frame_res[1]
        return frame_res * b

    def pix2frame_res(self, pix_frame_res, window_res) -> np.array:
        if pix_frame_res[0] / pix_frame_res[1] > 1:
            b = pix_frame_res[0] / window_res[0]
        else:
            b = pix_frame_res[1] / window_res[1]
        return pix_frame_res / b

    def pix2window_res(self, pix_window_res) -> np.array:
        if self.frame_res[0] / self.frame_res[1] > 1:
            b = pix_window_res[0] / self.frame_res[0]
        else:
            b = pix_window_res[1] / self.frame_res[1]
        return pix_window_res / b

    def get_cords(self) -> np.array:
        pix_window_res = np.array(self.parent.size().toTuple())
        window_res = self.pix2window_res(pix_window_res.astype(float))
        pix_cords = self.get_pix_cords()
        cords = self.pix_cords2cords(pix_cords.astype(float), window_res, pix_window_res.astype(float))
        return self.window_cords2frame_cords(cords, window_res)

    def pix_cords2cords(self, pix_cords, window_res, pix_window_res) -> np.array:
        b = window_res[0] / pix_window_res[0]
        cords = pix_cords * b
        return cords

    def cords2pix_cords(self, cords, window_res, pix_window_res) -> np.array:
        b = window_res[0] / pix_window_res[0]
        pix_cords = cords / b
        return pix_cords

    def window_cords2frame_cords(self, cords, window_res) -> np.array:
        frame_cords = cords - ((window_res - self.frame_res) / 2)
        return frame_cords

    def frame_cords2window_cords(self, cords, window_res) -> np.array:
        window_cords = cords + ((window_res - self.frame_res) / 2)
        return window_cords

    def get_limit_box(self):
        pix_window_res = np.array(self.parent.size().toTuple())
        frame_res = self.frame_res
        pix_frame_res = self.frame_res2pix(frame_res, pix_window_res)
        limit_box = np.vstack([np.zeros(2), pix_window_res])
        if np.isclose(pix_frame_res[0], pix_window_res[0], atol=0.5).all():
            limit_box[0, 1] = (pix_window_res[1] - pix_frame_res[1]) / 2
            limit_box[1, 1] = (pix_window_res[1] + pix_frame_res[1]) / 2 - 1
        else:
            limit_box[0, 0] = (pix_window_res[0] - pix_frame_res[0]) / 2
            limit_box[1, 0] = (pix_window_res[0] + pix_frame_res[0]) / 2 - 1
        return np.round(limit_box).astype(int)

    def resize_save_mod(self, event, point_1: QPoint, point_2: QPoint) -> None:
        limit_box = self.get_limit_box()
        if limit_box[0, 0] <= point_1.x() <= limit_box[1, 0] and limit_box[0, 1] <= point_1.y() <= limit_box[1, 1] and \
                limit_box[0, 0] <= point_2.x() <= limit_box[1, 0] and limit_box[0, 1] <= point_2.y() <= limit_box[1, 1]:
            self.move(point_1)
            self.resize(QSize(point_2.x() - point_1.x(), point_2.y() - point_1.y()))
        else:
            self.mousePressPos = event.position().toPoint()
        self.frame_update_func()

    def move_save_mod(self, event, point: QPoint) -> None:
        limit_box = self.get_limit_box()
        if limit_box[0, 0] <= point.x() <= limit_box[1, 0] - self.size().width() and \
                limit_box[0, 1] <= point.y() <= limit_box[1, 1] - self.size().height():
            self.move(point)
        else:
            self.mousePressPos = event.position().toPoint()
        self.frame_update_func()

    def set_cords(self, cords: np.array):
        pix_window_res = np.array(self.parent.size().toTuple())
        window_res = self.pix2window_res(pix_window_res.astype(float))
        cords = self.frame_cords2window_cords(cords.astype(float), window_res)
        pix_cords = self.cords2pix_cords(cords, window_res, pix_window_res.astype(float))
        self.set_pix_cords(pix_cords)

    def fix_cords(self, cords: np.array):
        limit_box = self.get_limit_box()
        cords = np.round(cords).astype(int)
        if np.array(cords[0, :] < cords[1, :]).all() and np.array(limit_box[0, :] < cords[1, :]).all():
            cords = np.clip(cords, limit_box[0, :], limit_box[1, :])
            return cords
        return None

    def set_frame_update_func(self, func=None):
        self.frame_update_func = func

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.data_update_func()

    def set_data_update_func(self, func=None):
        self.data_update_func = func
