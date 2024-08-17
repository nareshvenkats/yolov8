# Ultralytics YOLO 🚀, AGPL-3.0 license

from .ai_gym import AIGym
from .analytics import Analytics
from .distance_calculation import DistanceCalculation
from .heatmap import Heatmap
from .object_counter import ObjectCounter
from .parking_management import ParkingManagement, ParkingPtsSelection
from .queue_management import QueueManager
from .speed_estimation import SpeedEstimator
from .streamlit_inference import inference

__all__ = (
    "AIGym",
    "DistanceCalculation",
    "Heatmap",
    "ObjectCounter",
    "ParkingManagement",
    "ParkingPtsSelection",
    "QueueManager",
    "SpeedEstimator",
    "Analytics",
)


def extract_tracks(tracks):
    """
    Retrieves tracking results from the given data.

    Args:
        tracks (list): A list of tracks generated by the object tracking process.
    """
    boxes = tracks[0].boxes.xyxy.cpu()
    clss = tracks[0].boxes.cls.cpu().tolist()
    if tracks[0].boxes.id is not None:
        trk_ids = tracks[0].boxes.id.int().cpu().tolist()
        return boxes, clss, trk_ids
    else:
        return boxes, clss, None
