"""Utility functions for model loading and configuration.

This module provides helper functions for loading and configuring models used in the screenwise project.
The main functionality includes:

- Loading pre-trained Faster R-CNN models
- Modifying model architectures for custom number of classes
- Configuring model parameters and weights

Functions:
    get_model: Returns a modified Faster R-CNN model with custom number of output classes
"""

import torchvision
from torchvision.models.detection import FasterRCNN_ResNet50_FPN_Weights


def get_model(num_classes: int) -> torchvision.models.detection.FasterRCNN:
    """Get a pre-trained Faster R-CNN model with a modified head for custom number of classes.

    Args:
        num_classes (int): Number of classes to predict, including background class

    Returns:
        torchvision.models.detection.FasterRCNN: Modified Faster R-CNN model with custom classification head
    """
    # Load a pre-trained Faster R-CNN model
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=FasterRCNN_ResNet50_FPN_Weights.COCO_V1)

    # Get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features

    # Replace the head of the model with a new one (to adapt to our number of classes)
    model.roi_heads.box_predictor = torchvision.models.detection.faster_rcnn.FastRCNNPredictor(in_features, num_classes)

    return model
