import sys

import cv2
import ffmpeg
import numpy as np
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaFormat
from scipy.ndimage import gaussian_filter1d


class MetaData:
    nb_frames: int
    width: int
    height: int
    duration_ms: float

    def __init__(self, source: QUrl):
        self.probe = ffmpeg.probe(source.path(),
                                  cmd='ffprobe',
                                  timeout=None,
                                  select_streams='v',
                                  show_entries='frame=coded_picture_number,pkt_pts_time')
        self.video_stream = next((stream for stream in self.probe['streams'] if stream['codec_type'] == 'video'), None)
        self.nb_frames = len(self.probe['frames'])
        self.width = int(self.video_stream["width"])
        self.height = int(self.video_stream["height"])
        self.duration_ms = float(self.video_stream["duration"]) * 1000
        self.fpms = (self.nb_frames + 1) / self.duration_ms
        self.timestamps = np.zeros(len(self.probe['frames']), dtype=np.int)
        for frame in self.probe['frames']:
            self.timestamps[frame['coded_picture_number']] = int(float(frame['pkt_pts_time']) * 1000)

    def timestamp2frame_id(self, timestamp: int) -> int:
        idx = self.timestamps.searchsorted(timestamp)
        idx = np.clip(idx, 1, len(self.timestamps) - 1)
        left = self.timestamps[idx - 1]
        right = self.timestamps[idx]
        idx -= timestamp - left < right - timestamp
        return int(idx)


class MediaFormat:
    AVI = "video/x-msvideo"
    MP4 = 'video/mp4'
    is_windows = sys.platform == 'win32'
    mime_types: list

    def __init__(self):
        self.update_mini_types()

    def update_mini_types(self):
        self.mime_types = [
            QMediaFormat(f).mimeType()
            for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode)
        ]
        if self.is_windows and MediaFormat.AVI not in self.mime_types:
            self.mime_types.append(MediaFormat.AVI)
        elif MediaFormat.MP4 not in self.mime_types:
            self.mime_types.append(MediaFormat.MP4)


def gaussian_filter_rects(rects):
    arr = np.array(rects)
    x1 = np.array(arr[:, 0, 0])
    y1 = np.array(arr[:, 0, 1])
    x2 = np.array(arr[:, 1, 0])
    y2 = np.array(arr[:, 1, 1])

    x_c = np.round((x1 + x2) / 2).astype(int)
    y_c = np.round((y1 + y2) / 2).astype(int)
    x_l = np.round(x2 - x1).astype(int)
    y_l = np.round(y2 - y1).astype(int)
    y_g = gaussian_filter1d(gaussian_filter1d(y_c, 5), 5)
    x_g = gaussian_filter1d(gaussian_filter1d(x_c, 5), 5)
    y_lg = gaussian_filter1d(gaussian_filter1d(y_l, 10), 10)
    x_lg = gaussian_filter1d(gaussian_filter1d(x_l, 10), 10)

    n_x1 = list(np.round(x_g - x_lg / 2).astype(int))
    n_y1 = list(np.round(y_g - y_lg / 2).astype(int))
    n_x2 = list(np.round(n_x1 + x_lg).astype(int))
    n_y2 = list(np.round(n_y1 + y_lg).astype(int))

    return [[[n_x1[i], n_y1[i]], [n_x2[i], n_y2[i]]] for i in range(len(rects))]


def save_media(exist_path, save_path, rects, save_resolution: (int, int)):
    probe = ffmpeg.probe(exist_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    rects = gaussian_filter_rects(rects)
    r = save_resolution[0] / save_resolution[1]
    new_rects = []
    for rect in rects:
        w = rect[1][0] - rect[0][0]
        h = rect[1][1] - rect[0][1]
        x = 100
        if w > h:
            if w + x > width:
                w = width
            else:
                w += x
            n_w, n_h = w, w / r
        else:
            if h + x > height:
                h = height
            else:
                h += x
            n_w, n_h = h * r, h
        c_w = (rect[1][0] + rect[0][0]) / 2
        c_h = (rect[1][1] + rect[0][1]) / 2
        new_rect = [[round(c_w - n_w / 2), round(c_h - n_h / 2)], [round(c_w + n_w / 2), round(c_h + n_h / 2)]]
        if new_rect[0][0] < 0:
            new_rect[1][0] += abs(new_rect[0][0])
            new_rect[0][0] = 0
        if new_rect[0][1] < 0:
            new_rect[1][1] += abs(new_rect[0][1])
            new_rect[0][1] = 0
        if new_rect[1][0] >= width:
            new_rect[0][0] -= (new_rect[1][0] - width)
            new_rect[1][0] = width - 1
        if new_rect[1][1] >= height:
            new_rect[0][1] -= (new_rect[1][1] - height)
            new_rect[1][1] = height - 1
        new_rects.append(new_rect)

    process1 = (
        ffmpeg
        .input(exist_path)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run_async(pipe_stdout=True)
    )
    process2 = (
        ffmpeg
        .input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(save_resolution[0], save_resolution[1]))
        .output(ffmpeg.input(exist_path), save_path, pix_fmt='yuv422p')
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    i = 0
    while True:
        in_bytes = process1.stdout.read(width * height * 3)
        if not in_bytes:
            break
        in_frame = (np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3]))
        in_frame = in_frame[new_rects[i][0][1]:new_rects[i][1][1], new_rects[i][0][0]:new_rects[i][1][0]].copy()
        in_frame = cv2.resize(in_frame, save_resolution, interpolation=cv2.INTER_CUBIC)
        if in_frame.shape[1] != save_resolution[0] and in_frame.shape[0] != save_resolution[1]:
            process2.stdin.close()
            return False
        process2.stdin.write(in_frame.astype(np.uint8).tobytes())
        i += 1
    process2.stdin.close()
    return True


def ms_to_hours(millis):
    seconds, milliseconds = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}"
