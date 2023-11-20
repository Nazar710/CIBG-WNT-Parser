import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import torchvision.transforms as T
import torchvision

from ModelEvaluator import ModelEvaluator

## THIS class to SEE how column are predicted in images
## todo : add comments

class CoulmnDetector:
    def __init__(self, model_path, num_classes=2):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model(model_path, num_classes).to(self.device)
        self.model.eval()

    def load_model(self, model_path, num_classes):
        model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=num_classes)
        checkpoint = torch.load(model_path, map_location=self.device)

        # Check if the checkpoint contains the model state dictionary
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
                    print(f"Box Coordinates (Before NMS): x={x}, y={y}, width={w}, height={h}")

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
                print(f"Box Coordinates (AFTER NMS): x={x}, y={y}, width={w}, height={h}")
                ax.add_patch(rect)
            else:
                for box in boxes_nms:
                    x, y, w, h = box
                    rect = patches.Rectangle((x, y), w - x, h - y, linewidth=2, edgecolor='r', facecolor='none')
                    print(f"Box Coordinates (AFTER NMS): x={x}, y={y}, width={w}, height={h}")
                    ax.add_patch(rect)

        plt.show()


import os

# Specify the folder path containing your images and XML files
folder_path = "trainset"
model_path = "savedModel.pth"

# Loop through all files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".png") or file_name.endswith(".jpg"):
        # Assuming that your image files have either .png or .jpg extension
        image_path = os.path.join(folder_path, file_name)
        
        # Modify this part if your XML files have a specific naming convention
        xml_path = os.path.join(folder_path, file_name.replace(".png", ".xml").replace(".jpg", ".xml"))

        # Example usage:
        coulmn_detector = CoulmnDetector(model_path)
        coulmn_detector.plot_predicted_boxes(image_path, show_before_nms=False, resize_to_800=True)

        coulmn_detector_evaluator = ModelEvaluator(coulmn_detector)
        #precision, recall, mAP = coulmn_detector_evaluator.evaluate(image_path, xml_path, nms_threshold=0.5, resize_to_800=False)

        print(f"File: {file_name}")
        #print(f"Precision: {precision:.4f}")
        #print(f"Recall: {recall:.4f}")
        #print(f"mAP: {mAP:.4f}")
        print("-----------------------")

#FOR ONE TEST

# FileName = "DigiMV2020_QV3MJLR5MT_0_34126509_Jaarrekening_9632_Blijf Groep (Stichting).pdf_page_88"
# # Example usage:
# model_path = "F_model_epoch_1000.pth"
# image_path = f"data/{FileName}.png"

# coulmn_detector = CoulmnDetector(model_path)
# coulmn_detector.plot_predicted_boxes(image_path, show_before_nms=False, resize_to_800=True)

# # Example usage:
# xml_path = f"data/{FileName}.xml"

# coulmn_detector_evaluator = ModelEvaluator(coulmn_detector)
# precision, recall, mAP = coulmn_detector_evaluator.evaluate(image_path, xml_path, nms_threshold=0.5, resize_to_800=False)

# print(f"Precision: {precision:.4f}")
# print(f"Recall: {recall:.4f}")
# print(f"mAP: {mAP:.4f}")