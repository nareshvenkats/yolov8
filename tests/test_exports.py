# Ultralytics YOLO 🚀, AGPL-3.0 license

import shutil
import uuid
from itertools import product
from pathlib import Path

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
from tests import MODEL, SOURCE


def test_export_torchscript():
    """Test YOLO exports to TorchScript format."""
    file = YOLO(MODEL).export(format="torchscript", optimize=False, imgsz=32)
    YOLO(file)(SOURCE, imgsz=32)  # exported model inference


def test_export_onnx():
    """Test YOLO exports to ONNX format."""
    file = YOLO(MODEL).export(format="onnx", dynamic=True, imgsz=32)
    YOLO(file)(SOURCE, imgsz=32)  # exported model inference


@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="OpenVINO not supported in Python 3.12")
@pytest.mark.skipif(not TORCH_1_13, reason="OpenVINO requires torch>=1.13")
def test_export_openvino():
    """Test YOLO exports to OpenVINO format."""
    file = YOLO(MODEL).export(format="openvino", imgsz=32)
    YOLO(file)(SOURCE, imgsz=32)  # exported model inference


@pytest.mark.slow
@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="OpenVINO not supported in Python 3.12")
@pytest.mark.skipif(not TORCH_1_13, reason="OpenVINO requires torch>=1.13")
@pytest.mark.parametrize(
    "task, dynamic, int8, half, batch",
    [  # generate all combinations but exclude those where both int8 and half are True
        (task, dynamic, int8, half, batch)
        for task, dynamic, int8, half, batch in product(TASKS, [True, False], [True, False], [True, False], [1, 2])
        if not (int8 and half)  # exclude cases where both int8 and half are True
    ],
)
def test_export_openvino_matrix(task, dynamic, int8, half, batch):
    """Test YOLO exports to OpenVINO format."""
    file = YOLO(TASK2MODEL[task]).export(
        format="openvino",
        imgsz=32,
        dynamic=dynamic,
        int8=int8,
        half=half,
        batch=batch,
        data=TASK2DATA[task],
    )
    if WINDOWS:
        # Use unique filenames due to Windows file permissions bug possibly due to latent threaded use
        # See https://github.com/ultralytics/ultralytics/actions/runs/8957949304/job/24601616830?pr=10423
        file = Path(file)
        file = file.rename(file.with_stem(f"{file.stem}-{uuid.uuid4()}"))
    YOLO(file)([SOURCE] * batch, imgsz=64 if dynamic else 32)  # exported model inference
    with Retry(times=3, delay=1):  # retry in case of potential lingering multi-threaded file usage errors
        shutil.rmtree(file)


@pytest.mark.slow
@pytest.mark.parametrize("task, dynamic, int8, half, batch", product(TASKS, [True, False], [False], [False], [1, 2]))
def test_export_onnx_matrix(task, dynamic, int8, half, batch):
    """Test YOLO exports to ONNX format."""
    file = YOLO(TASK2MODEL[task]).export(
        format="onnx",
        imgsz=32,
        dynamic=dynamic,
        int8=int8,
        half=half,
        batch=batch,
    )
    YOLO(file)([SOURCE] * batch, imgsz=64 if dynamic else 32)  # exported model inference
    Path(file).unlink()  # cleanup


@pytest.mark.slow
@pytest.mark.parametrize("task, dynamic, int8, half, batch", product(TASKS, [False], [False], [False], [1, 2]))
def test_export_torchscript_matrix(task, dynamic, int8, half, batch):
    """Test YOLO exports to TorchScript format."""
    file = YOLO(TASK2MODEL[task]).export(
        format="torchscript",
        imgsz=32,
        dynamic=dynamic,
        int8=int8,
        half=half,
        batch=batch,
    )
    YOLO(file)([SOURCE] * 3, imgsz=64 if dynamic else 32)  # exported model inference at batch=3
    Path(file).unlink()  # cleanup


@pytest.mark.slow
@pytest.mark.skipif(not MACOS, reason="CoreML inference only supported on macOS")
@pytest.mark.skipif(not TORCH_1_9, reason="CoreML>=7.2 not supported with PyTorch<=1.8")
@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="CoreML not supported in Python 3.12")
@pytest.mark.parametrize(
    "task, dynamic, int8, half, batch",
    [  # generate all combinations but exclude those where both int8 and half are True
        (task, dynamic, int8, half, batch)
        for task, dynamic, int8, half, batch in product(TASKS, [False], [True, False], [True, False], [1])
        if not (int8 and half)  # exclude cases where both int8 and half are True
    ],
)
def test_export_coreml_matrix(task, dynamic, int8, half, batch):
    """Test YOLO exports to CoreML format."""
    file = YOLO(TASK2MODEL[task]).export(
        format="coreml",
        imgsz=32,
        dynamic=dynamic,
        int8=int8,
        half=half,
        batch=batch,
    )
    YOLO(file)([SOURCE] * batch, imgsz=32)  # exported model inference at batch=3
    shutil.rmtree(file)  # cleanup


# @pytest.mark.slow
@pytest.mark.skipif(not LINUX, reason="Test disabled as TF suffers from install conflicts on Windows and macOS")
@pytest.mark.parametrize(
    "task, dynamic, int8, half, batch",
    [  # generate all combinations but exclude those where both int8 and half are True
        (task, dynamic, int8, half, batch)
        for task, dynamic, int8, half, batch in product(TASKS, [False], [True, False], [True, False], [1])
        # for task, dynamic, int8, half, batch in product(["detect"], [False], [True], [False], [1])
        if not (int8 and half)  # exclude cases where both int8 and half are True
    ],
)
def test_export_tflite_matrix(task, dynamic, int8, half, batch):
    """Test YOLO exports to TFLite format."""
    file = YOLO(TASK2MODEL[task]).export(
        format="tflite",
        imgsz=32,
        dynamic=dynamic,
        int8=int8,
        half=half,
        batch=batch,
    )
    YOLO(file)([SOURCE] * batch, imgsz=32)  # exported model inference at batch=3
    Path(file).unlink()  # cleanup


@pytest.mark.skipif(not TORCH_1_9, reason="CoreML>=7.2 not supported with PyTorch<=1.8")
@pytest.mark.skipif(WINDOWS, reason="CoreML not supported on Windows")  # RuntimeError: BlobWriter not loaded
@pytest.mark.skipif(IS_RASPBERRYPI, reason="CoreML not supported on Raspberry Pi")
@pytest.mark.skipif(checks.IS_PYTHON_3_12, reason="CoreML not supported in Python 3.12")
def test_export_coreml():
    """Test YOLO exports to CoreML format."""
    if MACOS:
        file = YOLO(MODEL).export(format="coreml", imgsz=32)
        YOLO(file)(SOURCE, imgsz=32)  # model prediction only supported on macOS for nms=False models
    else:
        YOLO(MODEL).export(format="coreml", nms=True, imgsz=32)


@pytest.mark.skipif(not LINUX, reason="Test disabled as TF suffers from install conflicts on Windows and macOS")
def test_export_tflite():
    """
    Test YOLO exports to TFLite format.

    Note TF suffers from install conflicts on Windows and macOS.
    """
    model = YOLO(MODEL)
    file = model.export(format="tflite", imgsz=32)
    YOLO(file)(SOURCE, imgsz=32)


@pytest.mark.skipif(True, reason="Test disabled")
@pytest.mark.skipif(not LINUX, reason="TF suffers from install conflicts on Windows and macOS")
def test_export_pb():
    """
    Test YOLO exports to *.pb format.

    Note TF suffers from install conflicts on Windows and macOS.
    """
    model = YOLO(MODEL)
    file = model.export(format="pb", imgsz=32)
    YOLO(file)(SOURCE, imgsz=32)


@pytest.mark.skipif(True, reason="Test disabled as Paddle protobuf and ONNX protobuf requirementsk conflict.")
def test_export_paddle():
    """
    Test YOLO exports to Paddle format.

    Note Paddle protobuf requirements conflicting with onnx protobuf requirements.
    """
    YOLO(MODEL).export(format="paddle", imgsz=32)


@pytest.mark.slow
def test_export_ncnn():
    """Test YOLO exports to NCNN format."""
    file = YOLO(MODEL).export(format="ncnn", imgsz=32)
    YOLO(file)(SOURCE, imgsz=32)  # exported model inference
