from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Advanced Missing Person Identification System"
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: str = "missing_persons_db"
    upload_dir: str = "backend/uploads"
    face_model_dir: str = "backend/models"
    yunet_model_url: str = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
    sface_model_url: str = "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    frontend_base_url: str = "http://localhost:3000"

    strong_match_threshold: float = Field(default=0.85, ge=0, le=1)
    possible_match_threshold: float = Field(default=0.70, ge=0, le=1)
    min_face_similarity_for_possible: float = Field(default=0.62, ge=0, le=1)
    min_face_similarity_for_strong: float = Field(default=0.78, ge=0, le=1)
    face_detector_score_threshold: float = Field(default=0.9, ge=0, le=1)

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
