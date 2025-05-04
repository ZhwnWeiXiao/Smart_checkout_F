# modules/detection.py
import cv2
from ultralytics import YOLO
from typing import List, Tuple

class Detector:
    def __init__(self, model_path: str, conf: float = 0.3):
        self.model = YOLO(model_path)
        self.conf = conf

    def detect(self, frame) -> List[Tuple[int,int,int,int,float,int]]:
        """
        回傳 list of (x1, y1, x2, y2, confidence, class_id)
        且不印出 YOLOv8 自身的執行訊息
        """
        # 加上 verbose=False, show=False 來關閉內部輸出
        results = self.model(frame, conf=self.conf, verbose=False, show=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls  = int(box.cls[0])
                detections.append((x1,y1,x2,y2,conf,cls))
        return detections
