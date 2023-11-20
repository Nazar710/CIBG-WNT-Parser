import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import torchvision.transforms as T
import torchvision
from ModelEvaluator import ModelEvaluator
import os


## THIS class to SEE the check AP and AR

class ColumnDetector:
    def __init__(self, model_path, num_classes=2):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model(model_path, num_classes).to(self.device)
        self.model.eval()

    def load_model(self, model_path, num_classes):
        model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=num_classes)
        checkpoint = torch.load(model_path, map_location=self.device)

        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)

        return model

    def predict(self, image_path, resize_to_800=True):
        image = Image.open(image_path).convert("RGB")

        if resize_to_800:
            image = F.resize(image, (800, 800))

        image_tensor = F.to_tensor(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            prediction = self.model(image_tensor)

        return image, prediction

    def predict_batch(self, folder_path, resize_to_800=True):
        images = []
        predictions = []

        for filename in os.listdir(folder_path):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                image_path = os.path.join(folder_path, filename)
                image, prediction = self.predict(image_path, resize_to_800)
                images.append(image)
                predictions.append(prediction)

        return images, predictions

    def plot_predicted_boxes(self, image_path, nms_threshold=0.5, show_before_nms=True, resize_to_800=True):
        image, prediction = self.predict(image_path, resize_to_800)
        boxes = prediction[0]['boxes'].cpu().numpy()
        scores = prediction[0]['scores'].cpu().numpy()

        # Apply NMS
        keep = torchvision.ops.nms(torch.tensor(boxes), torch.tensor(scores), nms_threshold)
        boxes_nms = boxes[keep]

        # Plotting before NMS if show_before_nms is True
        if show_before_nms:
            fig, ax = plt.subplots(1, 2, figsize=(12, 6))
            ax[0].imshow(image)
            ax[0].set_title("Before NMS")

            if boxes.any():
                if len(boxes.shape) == 1:  # If only one box is detected
                    x, y, w, h = boxes
                    rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
                    #print(f"Box Coordinates (Before NMS): x={x}, y={y}, width={w}, height={h}")

                    ax[0].add_patch(rect)
                else:
                    for box in boxes:
                        x, y, w, h = box
                        rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
                        ax[0].add_patch(rect)

            # Plotting after NMS
            ax[1].imshow(image)
            ax[1].set_title("After NMS")
        else:
            # Plotting only after NMS if show_before_nms is False
            fig, ax = plt.subplots(1, 1, figsize=(6, 6))
            ax.imshow(image)
            ax.set_title("After NMS")

        if boxes_nms.any():
            if len(boxes_nms.shape) == 1:  # If only one box is detected after NMS
                x, y, w, h = boxes_nms
                rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
                #print(f"Box Coordinates (AFTER NMS): x={x}, y={y}, width={w}, height={h}")
                ax.add_patch(rect)
            else:
                for box in boxes_nms:
                    x, y, w, h = box
                    rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
                    #print(f"Box Coordinates (AFTER NMS): x={x}, y={y}, width={w}, height={h}")
                    ax.add_patch(rect)

        plt.show()

    def evaluate_batch(self, folder_path, annotations_folder, nms_threshold=0.5, resize_to_800=True):
        precisions = []
        recalls = []
        mAPs = []

        for filename in os.listdir(folder_path):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                image_path = os.path.join(folder_path, filename)
                xml_path = os.path.join(annotations_folder, f"{os.path.splitext(filename)[0]}.xml")

                column_detector_evaluator = ModelEvaluator(self)
                precision, recall, mAP = column_detector_evaluator.evaluate(image_path, xml_path, nms_threshold, resize_to_800)
                
                #print(f"Image: {filename}")
                #print(f"Precision: {precision:.4f}, Recall: {recall:.4f}, mAP: {mAP:.4f}")
                
                precisions.append(precision)
                recalls.append(recall)
                mAPs.append(mAP)

        average_precision = sum(precisions) / len(precisions)
        average_recall = sum(recalls) / len(recalls)
        average_mAP = sum(mAPs) / len(mAPs)

        # print("\nOverall Averages:")
        # print(f"Average Precision: {average_precision:.4f}")
        # print(f"Average Recall: {average_recall:.4f}")
        # print(f"Average mAP: {average_mAP:.4f}")

        return average_precision, average_recall, average_mAP


# Example usage for batch prediction and evaluation:
# model_path = "N_model_epoch_500.pth"
# image_folder = "data/"
# annotations_folder = "data/"

# column_detector = ColumnDetector(model_path)

# # Batch prediction
# images, predictions = column_detector.predict_batch(image_folder, resize_to_800=False)

# # Batch evaluation
# avg_precision, avg_recall, avg_mAP = column_detector.evaluate_batch(image_folder, annotations_folder, resize_to_800=False)

###########################

# List of model paths
#model_paths = ["z4N30_model_epoch_1.pth","z4N30_model_epoch_20.pth","z4N30_model_epoch_50.pth","z4N30_model_epoch_100.pth","z4N30_model_epoch_150.pth"]
model_paths = ["savedModel.pth"]

# Folder paths
image_folder = "traindata"
annotations_folder = "traindata"

for model_path in model_paths:
    print(f"\nProcessing model: {model_path}")
    
    # Initialize ColumnDetector with the current model
    column_detector = ColumnDetector(model_path)
    
    # Batch prediction
    images, predictions = column_detector.predict_batch(image_folder, resize_to_800=True)
    
    # Batch evaluation
    avg_precision, avg_recall, avg_mAP = column_detector.evaluate_batch(image_folder, annotations_folder, resize_to_800=False)
    
    # You can print or store the results for each model here
    print(f"\nAverage Precision for {model_path}: {avg_precision:.4f}")
    print(f"Average Recall for {model_path}: {avg_recall:.4f}")
    print(f"Average mAP for {model_path}: {avg_mAP:.4f}")
