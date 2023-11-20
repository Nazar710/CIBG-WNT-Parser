import os
import cv2
import torch
import torchvision
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from xml.etree import ElementTree as et
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2

from engine import train_one_epoch
import utils
import transforms as T

##THIS CLASS TO TRAIN RCNN


# Set up warning handling
import warnings
warnings.filterwarnings('ignore')

# Define constants
FILES_DIR = 'trainset/'

NUM_EPOCHS = 1000
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 800
LEARNING_RATE = 0.001
BATCH_SIZE = 1
LEARNING_RATE = 0.001
SAVE_MODEL_EPOCHS = [1, 20, 50, 70, 80, 100, 150, 200, 300]
NUM_WORKERS = 0
LR_STEP_SIZE = 500

NUM_CLASSES = 2
MOMENTUM = 0.9
WEIGHT_DECAY = 0.0005
LR_GAMMA = 0.1



class CoulmnImagesDataset(torch.utils.data.Dataset):

    def __init__(self, files_dir, width, height, transforms=None):
        
        self.transforms = transforms
        self.files_dir = files_dir
        self.height = height
        self.width = width
        
        # sorting the images for consistency
        # To get images, the extension of the filename is checked to be jpg
        self.imgs = [image for image in sorted(os.listdir(files_dir))
                        if image[-4:]=='.png']
        
        
        # classes: 0 index is reserved for background
        self.classes = ['','coulmn']

    def __getitem__(self, idx):

        img_name = self.imgs[idx]
        image_path = os.path.join(self.files_dir, img_name)

        # reading the images and converting them to correct size and color    
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)
        img_res = cv2.resize(img_rgb, (self.width, self.height), cv2.INTER_AREA)
        # diving by 255
        img_res /= 255.0 
        
        # annotation file
        annot_filename = img_name[:-4] + '.xml'
        annot_file_path = os.path.join(self.files_dir, annot_filename)
        
        boxes = []
        labels = []
        tree = et.parse(annot_file_path)
        root = tree.getroot()
        
        # cv2 image gives size as height x width
        wt = img.shape[1]
        ht = img.shape[0]
        
        # box coordinates for xml files are extracted and corrected for image size given
        for member in root.findall('object'):
            labels.append(self.classes.index(member.find('name').text))
            
            # bounding box
            xmin = int(member.find('bndbox').find('xmin').text)
            xmax = int(member.find('bndbox').find('xmax').text)
            
            ymin = int(member.find('bndbox').find('ymin').text)
            ymax = int(member.find('bndbox').find('ymax').text)
            
            
            xmin_corr = (xmin/wt)*self.width
            xmax_corr = (xmax/wt)*self.width
            ymin_corr = (ymin/ht)*self.height
            ymax_corr = (ymax/ht)*self.height
            
            boxes.append([xmin_corr, ymin_corr, xmax_corr, ymax_corr])
        
        # convert boxes into a torch.Tensor
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        
        # getting the areas of the boxes
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])

        # suppose all instances are not crowd
        iscrowd = torch.zeros((boxes.shape[0],), dtype=torch.int64)
        
        labels = torch.as_tensor(labels, dtype=torch.int64)


        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["area"] = area
        target["iscrowd"] = iscrowd
        # image_id
        image_id = torch.tensor([idx])
        target["image_id"] = image_id


        if self.transforms:
            
            sample = self.transforms(image = img_res,
                                     bboxes = target['boxes'],
                                     labels = labels)
            
            img_res = sample['image']
            target['boxes'] = torch.Tensor(sample['bboxes'])
            
            
            
        return img_res, target

    def __len__(self):
        return len(self.imgs)

def get_object_detection_model(num_classes):
    # load a model pre-trained pre-trained on COCO
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    # get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes) 
    # Load the saved model parameters
    #model.load_state_dict(torch.load("N24_model_epoch_700.pth")) 
    return model


#Data augmentation
# Send train=True fro training transforms and False for val/test transforms
def get_transform(train):
    
    if train:
        return A.Compose([
                            A.HorizontalFlip(0.5),
                     # ToTensorV2 converts image to pytorch tensor without div by 255
                            ToTensorV2(p=1.0) 
                        ], bbox_params={'format': 'pascal_voc', 'label_fields': ['labels']})
    else:
        return A.Compose([
                            ToTensorV2(p=1.0)
                        ], bbox_params={'format': 'pascal_voc', 'label_fields': ['labels']})
    

# use our dataset and defined transformations
dataset = CoulmnImagesDataset(FILES_DIR, IMAGE_WIDTH, IMAGE_HEIGHT, transforms= get_transform(train=True))

# define training and validation data loaders
data_loader = torch.utils.data.DataLoader(
    dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0,
    collate_fn=utils.collate_fn)

# to train on gpu if selected.
device = torch.device('cuda') 

# get the model using our helper function
model = get_object_detection_model(NUM_CLASSES)

# move model to the right device
model.to(device)

# construct an optimizer
params = [p for p in model.parameters() if p.requires_grad]
optimizer = torch.optim.SGD(params, lr=LEARNING_RATE,
                            momentum=MOMENTUM, weight_decay=WEIGHT_DECAY)

# and a learning rate scheduler which decreases the learning rate by
lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                step_size=LR_STEP_SIZE,
                                                gamma=LR_GAMMA)

print("WE ARE HERE ")

for epoch in range(NUM_EPOCHS):
    # training for one epoch
    print(f"We Are AT {epoch + 1}")

    train_one_epoch(model, optimizer, data_loader, device, epoch, print_freq=10)

    # Save the model at specific epochs
    if epoch + 1 in SAVE_MODEL_EPOCHS:
        torch.save(model.state_dict(), f'G_model_epoch_{epoch + 1}.pth')
        print(f"Model saved after epoch {epoch + 1}")
    
    # update the learning rate
    lr_scheduler.step()

torch.save(model.state_dict(), f'G_model_epoch_{NUM_EPOCHS}.pth')