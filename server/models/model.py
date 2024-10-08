from dataclasses import dataclass

from PIL import Image
import torch
from ultralytics import YOLO

from logger import logger


@dataclass
class ModelObject:
    box: tuple[int, int, int, int]
    name: str
    conf: float
    id: int = 0


class Model:
    def __init__(self, model_path: str, conf_threshold: int = 0.5, classes=None) -> None:
        self.conf_threshold = conf_threshold
        self.classes = classes
        if torch.cuda.is_available():
            torch.cuda.set_device(0)
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")
        logger.info(f"Using device: {device}")

        self.model = YOLO(model_path)
        self.model.to(device)

    def predict(self, image: Image) -> list[ModelObject]:
        try:
            result = self.model.track(image, persist=True)
            boxes = result[0].boxes.xywh.cpu()
            track_ids = result[0].boxes.id.int().cpu().tolist()
            cls = result[0].boxes.cls.cpu().tolist()
            detections = []
            for box, track_id, cls in zip(boxes, track_ids, cls):
                if self.classes is not None and cls not in self.classes:
                    continue
                x, y, w, h = box
                x1, y1, x2, y2 = int(x - w / 2), int(y - h / 2), int(x + w / 2), int(y + h / 2)
                logger.debug(f"Box: {x1, y1, x2, y2}, track_id: {track_id}, class: {cls}")
                detections.append(ModelObject(box=(x1, y1, x2, y2), name="person", conf=1.0, id=int(track_id)))
        except Exception as e:
            logger.error(f"Error in model prediction: {e}")
            detections = []
        return detections
