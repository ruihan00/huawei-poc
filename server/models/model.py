from dataclasses import dataclass

from PIL import Image
import torch
from ultralytics import YOLO

from logger import logger


@dataclass
class ModelResult:
    box: tuple[int, int, int, int]
    name: str
    conf: float


class Model:
    def __init__(self, model_path: str, conf_threshold: int = 0.5) -> None:
        self.conf_threshold = conf_threshold

        if torch.cuda.is_available():
            torch.cuda.set_device(0)
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")
        logger.info(f"Using device: {device}")

        self.model = YOLO(model_path)
        self.model.to(device)

    def predict(self, image: Image) -> list[ModelResult]:
        results = self.model(image)

        return results
