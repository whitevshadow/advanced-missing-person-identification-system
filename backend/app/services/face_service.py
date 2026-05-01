from functools import lru_cache
from pathlib import Path
from urllib.request import urlretrieve

import cv2
import numpy as np

from ..config import settings


def _ensure_model_file(path: Path, url: str) -> Path:
    if path.exists():
        return path

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        urlretrieve(url, str(path))
    except Exception as exc:
        raise RuntimeError(f"Failed to download model from {url}: {exc}") from exc

    return path


def _create_detector(model_path: str):
    if hasattr(cv2, "FaceDetectorYN_create"):
        return cv2.FaceDetectorYN_create(
            model_path,
            "",
            (320, 320),
            settings.face_detector_score_threshold,
            0.3,
            5000,
        )

    if hasattr(cv2, "FaceDetectorYN"):
        return cv2.FaceDetectorYN.create(
            model_path,
            "",
            (320, 320),
            settings.face_detector_score_threshold,
            0.3,
            5000,
        )

    raise RuntimeError(
        "OpenCV FaceDetectorYN is unavailable. Install opencv-contrib-python and restart."
    )


def _create_recognizer(model_path: str):
    if hasattr(cv2, "FaceRecognizerSF_create"):
        return cv2.FaceRecognizerSF_create(model_path, "")

    if hasattr(cv2, "FaceRecognizerSF"):
        return cv2.FaceRecognizerSF.create(model_path, "")

    raise RuntimeError(
        "OpenCV FaceRecognizerSF is unavailable. Install opencv-contrib-python and restart."
    )


@lru_cache(maxsize=1)
def _load_models():
    model_dir = Path(settings.face_model_dir)
    yunet_path = _ensure_model_file(
        model_dir / "face_detection_yunet_2023mar.onnx",
        settings.yunet_model_url,
    )
    sface_path = _ensure_model_file(
        model_dir / "face_recognition_sface_2021dec.onnx",
        settings.sface_model_url,
    )

    detector = _create_detector(str(yunet_path))
    recognizer = _create_recognizer(str(sface_path))
    return detector, recognizer


def _select_best_face(faces: np.ndarray) -> np.ndarray:
    if len(faces) == 1:
        return faces[0]

    ranked = sorted(
        faces,
        key=lambda face: (float(face[2]) * float(face[3])) + float(face[-1]),
        reverse=True,
    )
    return ranked[0]


def detect_and_embed(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Unable to read image file")

    detector, recognizer = _load_models()
    image_height, image_width = image.shape[:2]
    detector.setInputSize((image_width, image_height))

    _, faces = detector.detect(image)
    if faces is None or len(faces) == 0:
        raise ValueError("No face detected in image")

    best_face = _select_best_face(faces)

    try:
        aligned_face = recognizer.alignCrop(image, best_face)
        embedding = recognizer.feature(aligned_face)
    except cv2.error as exc:
        raise ValueError(f"Unable to encode detected face: {exc}") from exc

    if embedding is None:
        raise ValueError("No face embedding produced for this image")

    normalized = np.array(embedding, dtype=np.float32).reshape(-1)
    norm = np.linalg.norm(normalized)
    if norm > 0:
        normalized = normalized / norm

    return normalized
