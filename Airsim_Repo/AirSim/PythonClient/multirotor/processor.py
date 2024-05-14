import os

import supervision as sv
from ultralytics import YOLO

#this is supporting class to unitilze yolo model for demo
class MediaProcessor:
    def __init__(self):
        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoundingBoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()

    def process_video_frame(self, frame):
        model = YOLO(self._determine_model_path())
        results = model(frame)[0]
        detections = sv.Detections.from_ultralytics(results)
        detections = self.tracker.update_with_detections(detections)
        labels = [
            f"#{tracker_id} {results.names[class_id]}"
            for class_id, tracker_id in zip(detections.class_id, detections.tracker_id)
        ]
        annotated_frame = self.box_annotator.annotate(
            frame.copy(), detections=detections
        )
        return self.label_annotator.annotate(
            annotated_frame, detections=detections, labels=labels
        )

    def _determine_model_path(self):
        return (
            "runs/detect/train/weights/best.pt"
            if os.path.exists("runs/detect/train/weights/best.pt")
            else "yolov8n.pt"
        )
