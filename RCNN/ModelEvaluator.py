import xml.etree.ElementTree as ET
import numpy as np
from sklearn.metrics import precision_recall_curve, average_precision_score
import torch

from vision import torchvision

class ModelEvaluator:
    def __init__(self, model):
        self.model = model

    def parse_xml(self, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        boxes = []
        labels = []

        for obj in root.findall('object'):
            label = obj.find('name').text
            bbox = obj.find('bndbox')
            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)

            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(label)

        return np.array(boxes), labels

    def evaluate(self, image_path, xml_path, nms_threshold=0.5, resize_to_800=True):
        # Load ground truth
        gt_boxes, gt_labels = self.parse_xml(xml_path)

        # Map class labels to numeric IDs if needed
        label_mapping = {'coulmn': 1}  # Adjust as per your actual label mapping

        gt_labels_numeric = [label_mapping[label] for label in gt_labels]

        # Predict bounding boxes
        image, prediction = self.model.predict(image_path, resize_to_800)
        pred_boxes = prediction[0]['boxes'].cpu().numpy()
        pred_scores = prediction[0]['scores'].cpu().numpy()

        # Apply NMS
        keep = torchvision.ops.nms(torch.tensor(pred_boxes), torch.tensor(pred_scores), nms_threshold)
        pred_boxes_nms = pred_boxes[keep]
        pred_scores_nms = pred_scores[keep]

        # Ensure consistency in the number of samples
        min_samples = min(len(gt_labels_numeric), len(pred_scores_nms))
        gt_labels_numeric = gt_labels_numeric[:min_samples]
        pred_scores_nms = pred_scores_nms[:min_samples]

        #print(f"Ground Truth Labels (Numeric): {gt_labels_numeric}")

        # Calculate precision and recall
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        for gt_box, gt_label in zip(gt_boxes, gt_labels_numeric):
            iou = self.calculate_iou(gt_box, pred_boxes_nms)
            if np.max(iou) >= nms_threshold:
                true_positives += 1
            else:
                false_negatives += 1

        false_positives = len(pred_boxes_nms) - true_positives

        #print(f"True Positives: {true_positives}")
        #print(f"False Positives: {false_positives}")
        #print(f"False Negatives: {false_negatives}")

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

        # Calculate mAP
        average_precision = average_precision_score(gt_labels_numeric, pred_scores_nms)

        return precision, recall, average_precision



    def calculate_iou(self, box1, box2):
        x1 = np.maximum(box1[0], box2[:, 0])
        y1 = np.maximum(box1[1], box2[:, 1])
        x2 = np.minimum(box1[2], box2[:, 2])
        y2 = np.minimum(box1[3], box2[:, 3])

        intersection = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area_box2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])
        union = area_box1 + area_box2 - intersection

        iou = intersection / np.maximum(union, 1e-10)
        return iou


