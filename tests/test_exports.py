# Ultralytics YOLO 🚀, AGPL-3.0 license

import shutil
from itertools import product

import pytest

from ultralytics import YOLO
from ultralytics.cfg import TASK2DATA, TASK2MODEL, TASKS
from ultralytics.utils import (
    IS_RASPBERRYPI,
    LINUX,
    MACOS,
    WINDOWS,
    Retry,
    checks,
)
from ultralytics.utils.torch_utils import TORCH_1_9, TORCH_1_13

from . import MODEL, SOURCE

# Constants
EXPORT_PARAMETERS_LIST = [  # generate all combinations but exclude those where both int8 and half are True
    (task, dynamic, int8, half, batch)
    for task, dynamic, int8, half, batch in product(TASKS, [True, False], [True, False], [True, False], [1, 2])
    if not (int8 and half)  # exclude cases where both int8 and half are True
]


def test_export_torchscript():
    """Test exporting the YOLO model to TorchScript format."""
    f = YOLO(MODEL).export(format="torchscript", optimize=False, imgsz=32)
    YOLO(f)(SOURCE, imgsz=32)  # exported model inference


def test_export_onnx():
    """Test exporting the YOLO model to ONNX format."""
    f = YOLO(MODEL).export(format="onnx", dynamic=True, imgsz=32)
    YOLO(f)(SOURCE, imgsz=32)  # exported model inference


@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="OpenVINO not supported in Python 3.12")
@pytest.mark.skipif(not TORCH_1_13, reason="OpenVINO requires torch>=1.13")
def test_export_openvino():
    """Test exporting the YOLO model to OpenVINO format."""
    f = YOLO(MODEL).export(format="openvino", imgsz=32)
    YOLO(f)(SOURCE, imgsz=32)  # exported model inference


# @pytest.mark.slow
@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="OpenVINO not supported in Python 3.12")
@pytest.mark.skipif(not TORCH_1_13, reason="OpenVINO requires torch>=1.13")
@pytest.mark.parametrize("task, dynamic, int8, half, batch", EXPORT_PARAMETERS_LIST)
def test_export_openvino_matrix(task, dynamic, int8, half, batch):
    """Test exporting the YOLO model to OpenVINO format."""
    f = YOLO(TASK2MODEL[task]).export(
        format="openvino",
        imgsz=32,
        dynamic=dynamic,
        int8=int8,
        half=half,
        batch=batch,
        data=TASK2DATA[task],
    )
    YOLO(f)([SOURCE] * batch, imgsz=64 if dynamic else 32)  # exported model inference
    with Retry(times=3, delay=1):  # retry in case of potential lingering multi-threaded file usage errors
        shutil.rmtree(f)


@pytest.mark.skipif(not TORCH_1_9, reason="CoreML>=7.2 not supported with PyTorch<=1.8")
@pytest.mark.skipif(WINDOWS, reason="CoreML not supported on Windows")  # RuntimeError: BlobWriter not loaded
@pytest.mark.skipif(IS_RASPBERRYPI, reason="CoreML not supported on Raspberry Pi")
@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="CoreML not supported in Python 3.12")
def test_export_coreml():
    """Test exporting the YOLO model to CoreML format."""
    if MACOS:
        f = YOLO(MODEL).export(format="coreml", imgsz=32)
        YOLO(f)(SOURCE, imgsz=32)  # model prediction only supported on macOS for nms=False models
    else:
        YOLO(MODEL).export(format="coreml", nms=True, imgsz=32)


@pytest.mark.skipif(not LINUX, reason="Test disabled as TF suffers from install conflicts on Windows and macOS")
def test_export_tflite():
    """
    Test exporting the YOLO model to TFLite format.

    Note TF suffers from install conflicts on Windows and macOS.
    """
    model = YOLO(MODEL)
    f = model.export(format="tflite", imgsz=32)
    YOLO(f)(SOURCE, imgsz=32)


@pytest.mark.skipif(True, reason="Test disabled")
@pytest.mark.skipif(not LINUX, reason="TF suffers from install conflicts on Windows and macOS")
def test_export_pb():
    """
    Test exporting the YOLO model to *.pb format.

    Note TF suffers from install conflicts on Windows and macOS.
    """
    model = YOLO(MODEL)
    f = model.export(format="pb", imgsz=32)
    YOLO(f)(SOURCE, imgsz=32)


@pytest.mark.skipif(True, reason="Test disabled as Paddle protobuf and ONNX protobuf requirementsk conflict.")
def test_export_paddle():
    """
    Test exporting the YOLO model to Paddle format.

    Note Paddle protobuf requirements conflicting with onnx protobuf requirements.
    """
    YOLO(MODEL).export(format="paddle", imgsz=32)


@pytest.mark.slow
def test_export_ncnn():
    """Test exporting the YOLO model to NCNN format."""
    f = YOLO(MODEL).export(format="ncnn", imgsz=32)
    YOLO(f)(SOURCE, imgsz=32)  # exported model inference
