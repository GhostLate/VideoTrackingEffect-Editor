import ctypes
from dataclasses import dataclass
from functools import cached_property

import numpy as np
from PySide6.QtCore import QObject, Signal, Property, QSize
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import QVideoFrameFormat, QVideoFrame

"""
def q_video_frame2q_image(video_frame):
    image_format = QVideoFrameFormat.imageFormatFromPixelFormat(
        video_frame.pixelFormat()
    )
    if image_format == QImage.Format.Format_Invalid:
        print("Invalid format")
        return
    plane = 0
    ptr = video_frame.bits(plane)
    image = QImage(
        ptr if isinstance(ptr, memoryview) else int(ptr),
        video_frame.width(),
        video_frame.height(),
        image_format,
    )
    return image
"""


@dataclass(frozen=True)
class _QVideoFrameInterface:
    video_frame: QVideoFrame
    plane: int = 0

    @cached_property
    def __array_interface__(self):
        data = self.video_frame.bits(self.plane)
        if not isinstance(data, memoryview):
            data.setsize(self.video_frame.mappedBytes(self.plane))
        return dict(
            shape=(self.video_frame.height(), self.video_frame.width(), 4),
            typestr="|u1",
            data=data,
            strides=(self.video_frame.bytesPerLine(self.plane), 4, 1),
            version=3,
        )


def q_video_frame2numpy(video_frame):
    return np.asarray(_QVideoFrameInterface(video_frame))


def write_qvideoframe_from_ndarray(video_frame, np_image, with_ctypes=True):
    plane = 0
    data = video_frame.bits(plane)
    assert np_image.size == video_frame.mappedBytes(plane), "Must be same size!!!"
    if with_ctypes:
        ctypes.memmove(
            (ctypes.c_ubyte * len(data)).from_buffer(data)
            if isinstance(data, memoryview)
            else int(data),
            np_image.ctypes.data,
            video_frame.mappedBytes(plane),
        )
    else:
        if not isinstance(data, memoryview):
            data.setsize(video_frame.mappedBytes(plane))
        data[:] = bytearray(np_image)


def build_video_frame(size):
    video_frame_format = QVideoFrameFormat.PixelFormat.Format_BGRA8888
    video_frame = QVideoFrame(QVideoFrameFormat(size, video_frame_format))
    if not video_frame.isValid() or not video_frame.map(QVideoFrame.MapMode.WriteOnly):
        raise RuntimeError(f"QVideoFrame is invalid or not writable")
    return video_frame


def q_image2numpy(video_frame):
    return np.asarray(_QImageInterface(video_frame))


@dataclass(frozen=True)
class _QImageInterface:
    image: QImage

    @cached_property
    def __array_interface__(self):
        data = self.image.bits()
        if not isinstance(data, memoryview):
            data.setsize(self.image.sizeInBytes())
        return dict(
            shape=(self.image.height(), self.image.width(), 4),
            typestr="|u1",
            data=data,
            strides=(self.image.bytesPerLine(), 4, 1),
            version=3,
        )


class FrameProvider(QObject):
    video_sink_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._video_sink = None

    @Property(QObject, notify=video_sink_changed)
    def video_sink(self):
        return self._video_sink

    @video_sink.setter
    def video_sink(self, video_sink):
        if self.video_sink is not None:
            self.video_sink.destroyed.disconnect(self._handle_destroyed)
            if self.video_sink.parent() is self:
                self.video_sink.setParent(None)
                self.video_sink.deleteLater()
        self._video_sink = video_sink
        video_sink.destroyed.connect(self._handle_destroyed)
        self.video_sink_changed.emit()

    def write_frame(self, image_frame):
        if self.video_sink is None or image_frame is None or len(image_frame.shape) != 3:
            print("video_sink or image_format is None")
            return
        height, width, _ = image_frame.shape
        try:
            video_frame = build_video_frame(QSize(width, height))
        except RuntimeError:
            pass
        else:
            write_qvideoframe_from_ndarray(video_frame, image_frame, with_ctypes=True)
            video_frame.unmap()
            self.video_sink.setVideoFrame(video_frame)

    def _handle_destroyed(self):
        self._video_sink = None
