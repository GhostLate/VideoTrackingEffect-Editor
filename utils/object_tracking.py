import cv2
import numpy as np


class ObjectTracker:
    frame_shape: np.array
    bbox_exist: bool
    bbox: np.array

    def __init__(self, tracker_type=None, res_rate=1):
        """
        tracker_types: 'DaSiamRPN', 'CSRT'
        """
        self.res_rate = res_rate
        if not tracker_type and tracker_type == 'DaSiamRPN':
            params = cv2.TrackerDaSiamRPN_Params()
            params.model = "./models/dasiamrpn/dasiamrpn_model.onnx"
            params.kernel_cls1 = "./models/dasiamrpn/dasiamrpn_kernel_cls1.onnx"
            params.kernel_r1 = "./models/dasiamrpn/dasiamrpn_kernel_r1.onnx"
            self.tracker = cv2.TrackerDaSiamRPN_create(params)
        else:
            self.tracker = cv2.TrackerCSRT_create()

    def prepare_frame(self, frame):
        if frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        elif len(frame.shape) == 2 or frame.shape[2] == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        return cv2.resize(frame, (frame.shape[1] // self.res_rate, frame.shape[0] // self.res_rate),
                          interpolation=cv2.INTER_CUBIC)

    def update_frame(self, frame):
        self.bbox_exist, bbox = self.tracker.update(self.prepare_frame(frame))
        if self.bbox_exist:
            bbox = np.round(format_bbox(bbox) * self.res_rate).astype(int)
            bbox = self.fix_bbox(bbox)
            if bbox is not None:
                self.bbox = bbox
                return self.bbox_exist, self.bbox
        return False, self.bbox

    def update_roi(self, frame, bbox):
        self.frame_shape = np.array(frame.shape)
        bbox = self.fix_bbox(bbox)
        if bbox is not None:
            bbox = np.round(bbox / self.res_rate).astype(int)
            self.bbox = bbox
            self.bbox_exist = self.tracker.init(self.prepare_frame(frame), flatten_bbox(bbox))
            return self.bbox_exist
        else:
            return False

    def fix_bbox(self, bbox: np.array):
        bbox[:, 0] = np.clip(bbox[:, 0], 0, self.frame_shape[1] - 1)
        bbox[:, 1] = np.clip(bbox[:, 1], 0, self.frame_shape[0] - 1)
        if np.array(bbox[0, :] < bbox[1, :]).all():
            return bbox
        return None


def flatten_bbox(bbox: np.array):
    return [bbox[0][0], bbox[0][1], bbox[1][0] - bbox[0][0], bbox[1][1] - bbox[0][1]]


def format_bbox(bbox: [int, int, int, int]):
    return np.array(([bbox[0], bbox[1]], [bbox[0] + bbox[2], bbox[1] + bbox[3]]))
