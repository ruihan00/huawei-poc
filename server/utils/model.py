import base64
import io
from typing import List
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

class Model:
    def __init__(self, model_path: str) -> None:
        self.model = YOLO(model_path)

    def predict(self, base64_str: str) -> str:
        """
        Perform prediction on a base64-encoded image and return the annotated image as a base64 string.

        Args:
            base64_str (str): The base64-encoded image string.

        Returns:
            str: The base64-encoded string of the annotated image.
        """
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        results = self.model(image)
        boxes = results[0].boxes.xyxy.tolist()
        classes = results[0].boxes.cls.tolist()
        names = results[0].names
        confidences = results[0].boxes.conf.tolist()

        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for box, cls, conf in zip(boxes, classes, confidences):
            x1, y1, x2, y2 = box
            confidence = conf
            name = names[int(cls)]
            label = f"{name}: {confidence:.2f}"
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
            text_bbox = draw.textbbox((x1, y1), label, font=font)
            text_background = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
            draw.rectangle(text_background, fill="red")
            draw.text((x1, y1), label, fill="white", font=font)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return base64_image

    @staticmethod
    def save_base64_to_image(base64_str: str, output_path: str) -> None:
        """
        Save a base64-encoded image to a file.

        Args:
            base64_str (str): The base64-encoded image string.
            output_path (str): The path where the image will be saved.
        """
        image_data = base64.b64decode(base64_str)
        with open(output_path, 'wb') as f:
            f.write(image_data)

