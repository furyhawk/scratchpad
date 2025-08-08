# %% [markdown]
# [![Roboflow Notebooks](https://media.roboflow.com/notebooks/template/bannertest2-2.png?ik-sdk-version=javascript-1.4.3&updatedAt=1672932710194)](https://github.com/roboflow/notebooks)
# 
# # How to Train RT-DETR on Custom Dataset
# 
# ---
# 
# [![arXiv](https://img.shields.io/badge/arXiv-2304.08069-b31b1b.svg)](https://arxiv.org/pdf/2304.08069.pdf)
# [![GitHub](https://badges.aleen42.com/src/github.svg)](https://github.com/lyuwenyu/RT-DETR)
# 
# RT-DETR, short for "Real-Time DEtection TRansformer", is a computer vision model developed by Peking University and Baidu. In their paper, "DETRs Beat YOLOs on Real-time Object Detection" the authors claim that RT-DETR can outperform YOLO models in object detection, both in terms of speed and accuracy. The model has been released under the Apache 2.0 license, making it a great option, especially for enterprise projects.
# 
# ![RT-DETR Figure.1](https://storage.googleapis.com/com-roboflow-marketing/notebooks/examples/rt-detr-figure-1.png)
# 
# Recently, RT-DETR was added to the `transformers` library, significantly simplifying its fine-tuning process. In this tutorial, we will show you how to train RT-DETR on a custom dataset.

# %% [markdown]
# ## Setup

# %% [markdown]
# ### Configure your API keys
# 
# To fine-tune RT-DETR, you need to provide your HuggingFace Token and Roboflow API key. Follow these steps:
# 
# - Open your [`HuggingFace Settings`](https://huggingface.co/settings) page. Click `Access Tokens` then `New Token` to generate new token.
# - Go to your [`Roboflow Settings`](https://app.roboflow.com/settings/api) page. Click `Copy`. This will place your private key in the clipboard.
# - In Colab, go to the left pane and click on `Secrets` (🔑).
#     - Store HuggingFace Access Token under the name `HF_TOKEN`.
#     - Store Roboflow API Key under the name `ROBOFLOW_API_KEY`.

# %% [markdown]
# ### Select the runtime
# 
# Let's make sure that we have access to GPU. We can use `nvidia-smi` command to do that. In case of any problems navigate to `Edit` -> `Notebook settings` -> `Hardware accelerator`, set it to `L4 GPU`, and then click `Save`.

# %%
# !nvidia-smi

# %% [markdown]
# **NOTE:** To make it easier for us to manage datasets, images and models we create a `HOME` constant.

# %%
import os
HOME = os.getcwd()
print("HOME:", HOME)

# %% [markdown]
# ### Install dependencies

# %%
# !pip install -q git+https://github.com/huggingface/transformers.git
# !pip install -q git+https://github.com/roboflow/supervision.git
# !pip install -q accelerate
# !pip install -q roboflow
# !pip install -q torchmetrics
# !pip install -q "albumentations>=1.4.5"
# !pip install -q python-dotenv

# %% [markdown]
# ### Imports

# %%
import torch
import requests
import os

import numpy as np
import supervision as sv
import albumentations as A

from PIL import Image
from pprint import pprint
from roboflow import Roboflow
from dataclasses import dataclass, replace
from dotenv import load_dotenv
# from google.colab import userdata
from torch.utils.data import Dataset
from transformers import (
    AutoImageProcessor,
    AutoModelForObjectDetection,
    TrainingArguments,
    Trainer
)
from torchmetrics.detection.mean_ap import MeanAveragePrecision

# %% [markdown]
# ## Inference with pre-trained RT-DETR model

# %%
# @title Load model

# Prefer a locally fine-tuned checkpoint if available, else fall back to HF
DEFAULT_CHECKPOINT = "PekingU/rtdetr_r50vd_coco_o365"
LOCAL_CHECKPOINT_DIR = "./rt-detr-rust"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _is_valid_local_checkpoint(path: str) -> bool:
    try:
        if not os.path.isdir(path):
            return False
        # Heuristic: presence of config and at least one model weight file
        has_config = os.path.isfile(os.path.join(path, "config.json"))
        has_weights = any(
            os.path.isfile(os.path.join(path, fname))
            for fname in ("pytorch_model.bin", "model.safetensors")
        )
        return has_config and has_weights
    except Exception:
        return False

# Decide which checkpoint to use
_preferred = LOCAL_CHECKPOINT_DIR if _is_valid_local_checkpoint(LOCAL_CHECKPOINT_DIR) else DEFAULT_CHECKPOINT
CHECKPOINT = _preferred

try:
    model = AutoModelForObjectDetection.from_pretrained(CHECKPOINT).to(DEVICE)
    processor = AutoImageProcessor.from_pretrained(CHECKPOINT)
    print(f"Model source: {'local' if CHECKPOINT == LOCAL_CHECKPOINT_DIR else 'huggingface'} -> {CHECKPOINT}")
except Exception as e:
    # Fallback to DEFAULT_CHECKPOINT if local load fails for any reason
    if CHECKPOINT != DEFAULT_CHECKPOINT:
        print(f"Failed to load local checkpoint at {CHECKPOINT} ({e}); falling back to {DEFAULT_CHECKPOINT}.")
        CHECKPOINT = DEFAULT_CHECKPOINT
        model = AutoModelForObjectDetection.from_pretrained(CHECKPOINT).to(DEVICE)
        processor = AutoImageProcessor.from_pretrained(CHECKPOINT)
        print(f"Model source: huggingface -> {CHECKPOINT}")
    else:
        raise

# %%
# @title Run inference

URL = "https://media.roboflow.com/notebooks/examples/dog.jpeg"

image = Image.open(requests.get(URL, stream=True).raw)
inputs = processor(image, return_tensors="pt").to(DEVICE)

with torch.no_grad():
    outputs = model(**inputs)

w, h = image.size
results = processor.post_process_object_detection(
    outputs, target_sizes=[(h, w)], threshold=0.3)

# %%
# @title Display result with NMS

detections = sv.Detections.from_transformers(results[0])
labels = [
    model.config.id2label[class_id]
    for class_id
    in detections.class_id
]

annotated_image = image.copy()
annotated_image = sv.BoxAnnotator().annotate(annotated_image, detections)
annotated_image = sv.LabelAnnotator().annotate(annotated_image, detections, labels=labels)
annotated_image.thumbnail((600, 600))
annotated_image

# %%
# @title Display result with NMS

detections = sv.Detections.from_transformers(results[0]).with_nms(threshold=0.1)
labels = [
    model.config.id2label[class_id]
    for class_id
    in detections.class_id
]

annotated_image = image.copy()
annotated_image = sv.BoxAnnotator().annotate(annotated_image, detections)
annotated_image = sv.LabelAnnotator().annotate(annotated_image, detections, labels=labels)
annotated_image.thumbnail((600, 600))
annotated_image

# %% [markdown]
# ## Fine-tune RT-DETR on custom dataset

# %%
# @title Download dataset from Roboflow Universe

# Load environment variables from .env file
load_dotenv()

ROBOFLOW_API_KEY = os.getenv('ROBOFLOW_API_KEY')
if not ROBOFLOW_API_KEY:
    raise ValueError("ROBOFLOW_API_KEY not found in environment variables. Please check your .env file.")

rf = Roboflow(api_key=ROBOFLOW_API_KEY)

project = rf.workspace("test-0dgvp").project("rust-rt3ec")
version = project.version(1)
dataset = version.download("coco")

# %%
ds_train = sv.DetectionDataset.from_coco(
    images_directory_path=f"{dataset.location}/train",
    annotations_path=f"{dataset.location}/train/_annotations.coco.json",
)
ds_valid = sv.DetectionDataset.from_coco(
    images_directory_path=f"{dataset.location}/valid",
    annotations_path=f"{dataset.location}/valid/_annotations.coco.json",
)
ds_test = sv.DetectionDataset.from_coco(
    images_directory_path=f"{dataset.location}/test",
    annotations_path=f"{dataset.location}/test/_annotations.coco.json",
)

print(f"Number of training images: {len(ds_train)}")
print(f"Number of validation images: {len(ds_valid)}")
print(f"Number of test images: {len(ds_test)}")

# %%
# @title Display dataset sample

GRID_SIZE = 5

def annotate(image, annotations, classes):
    labels = [
        classes[class_id]
        for class_id
        in annotations.class_id
    ]

    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator(text_scale=1, text_thickness=2)

    annotated_image = image.copy()
    annotated_image = bounding_box_annotator.annotate(annotated_image, annotations)
    annotated_image = label_annotator.annotate(annotated_image, annotations, labels=labels)
    return annotated_image

annotated_images = []
for i in range(GRID_SIZE * GRID_SIZE):
    _, image, annotations = ds_train[i]
    annotated_image = annotate(image, annotations, ds_train.classes)
    annotated_images.append(annotated_image)

grid = sv.create_tiles(
    annotated_images,
    grid_size=(GRID_SIZE, GRID_SIZE),
    single_tile_size=(400, 400),
    tile_padding_color=sv.Color.WHITE,
    tile_margin_color=sv.Color.WHITE
)
sv.plot_image(grid, size=(10, 10))

# %% [markdown]
# ### Preprocess the data
# 
# To finetune a model, you must preprocess the data you plan to use to match precisely the approach used for the pre-trained model. [AutoImageProcessor](https://huggingface.co/docs/transformers/main/en/model_doc/auto#transformers.AutoImageProcessor) takes care of processing image data to create `pixel_values`, `pixel_mask`, and `labels` that a DETR model can train with. The image processor has some attributes that you won't have to worry about:
# 
# - `image_mean = [0.485, 0.456, 0.406 ]`
# - `image_std = [0.229, 0.224, 0.225]`
# 
# These are the mean and standard deviation used to normalize images during the model pre-training. These values are crucial to replicate when doing inference or finetuning a pre-trained image model.
# 
# Instantiate the image processor from the same checkpoint as the model you want to finetune.

# %%
IMAGE_SIZE = 480

processor = AutoImageProcessor.from_pretrained(
    CHECKPOINT,
    do_resize=True,
    size={"width": IMAGE_SIZE, "height": IMAGE_SIZE},
)

# %% [markdown]
# Before passing the images to the `processor`, apply two preprocessing transformations to the dataset:
# 
# - Augmenting images
# - Reformatting annotations to meet RT-DETR expectations
# 
# First, to make sure the model does not overfit on the training data, you can apply image augmentation with any data augmentation library. Here we use [Albumentations](https://albumentations.ai/docs/). This library ensures that transformations affect the image and update the bounding boxes accordingly.

# %%
train_augmentation_and_transform = A.Compose(
    [
        A.Perspective(p=0.1),
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.5),
        A.HueSaturationValue(p=0.1),
    ],
    bbox_params=A.BboxParams(
        format="pascal_voc",
        label_fields=["category"],
        clip=True,
        min_area=25,
        min_visibility=0.3  # Ensure at least 30% of the box is visible after transformation
    ),
)

valid_transform = A.Compose(
    [A.NoOp()],
    bbox_params=A.BboxParams(
        format="pascal_voc",
        label_fields=["category"],
        clip=True,
        min_area=1,
        min_visibility=0.1  # Minimal visibility requirement for validation
    ),
)

# %%
# @title Visualize some augmented images

IMAGE_COUNT = 5

for i in range(IMAGE_COUNT):
    _, image, annotations = ds_train[i]

    output = train_augmentation_and_transform(
        image=image,
        bboxes=annotations.xyxy,
        category=annotations.class_id
    )

    augmented_image = output["image"]
    
    # Create new annotations with only the necessary fields
    # Filter out any data fields that might have mismatched shapes
    augmented_annotations = sv.Detections(
        xyxy=np.array(output["bboxes"]),
        class_id=np.array(output["category"])
    )

    annotated_images = [
        annotate(image, annotations, ds_train.classes),
        annotate(augmented_image, augmented_annotations, ds_train.classes)
    ]
    grid = sv.create_tiles(
        annotated_images,
        titles=['original', 'augmented'],
        titles_scale=0.5,
        single_tile_size=(400, 400),
        tile_padding_color=sv.Color.WHITE,
        tile_margin_color=sv.Color.WHITE
    )
    sv.plot_image(grid, size=(6, 6))

# %% [markdown]
# The `processor` expects the annotations to be in the following format: `{'image_id': int, 'annotations': List[Dict]}`, where each dictionary is a COCO object annotation. Let's add a function to reformat annotations for a single example:

# %%
class PyTorchDetectionDataset(Dataset):
    def __init__(self, dataset: sv.DetectionDataset, processor, transform: A.Compose = None):
        self.dataset = dataset
        self.processor = processor
        self.transform = transform
        # Precompute valid indices where annotations exist
        self.valid_indices = []
        for idx in range(len(dataset)):
            _, _, annotations = dataset[idx]
            boxes = annotations.xyxy
            valid_boxes_mask = (boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])
            if valid_boxes_mask.any():
                self.valid_indices.append(idx)
        if not self.valid_indices:
            raise ValueError("No valid images found in the dataset")
            
    def __len__(self):
        return len(self.valid_indices)
    
    def __getitem__(self, idx):
        """Return a processed training example.

        Important: Do not raise StopIteration here. DataLoader expects __getitem__
        to always return for valid indices. We instead retry augmentation a few
        times and, if needed, fall back to the un-augmented sample which may
        contain zero boxes (supported by HF processors/models).
        """
        # Get the actual index from the valid indices
        dataset_idx = self.valid_indices[idx]
        _, image, annotations = self.dataset[dataset_idx]

        # Convert image to RGB numpy array (dataset returns BGR)
        image = image[:, :, ::-1]
        boxes = annotations.xyxy
        categories = annotations.class_id

        # Filter out invalid bounding boxes
        valid_boxes_mask = (boxes[:, 2] > boxes[:, 0]) & (boxes[:, 3] > boxes[:, 1])
        boxes = boxes[valid_boxes_mask]
        categories = categories[valid_boxes_mask]

        # Apply augmentation with a few retries to keep at least one box
        if self.transform is not None:
            last_error = None
            for _ in range(5):
                try:
                    transformed = self.transform(
                        image=image,
                        bboxes=boxes,
                        category=categories,
                    )
                    aug_image = transformed["image"]
                    aug_boxes = transformed["bboxes"]
                    aug_categories = transformed["category"]

                    # Normalize types
                    if isinstance(aug_boxes, list):
                        aug_boxes = np.array(aug_boxes, dtype=float)
                    if isinstance(aug_categories, list):
                        aug_categories = np.array(aug_categories, dtype=int)

                    # Keep if any boxes remain, else retry
                    if aug_boxes is not None and len(aug_boxes) > 0:
                        image = aug_image
                        boxes = aug_boxes
                        categories = aug_categories
                        break
                except Exception as e:
                    # Keep error for context and retry
                    last_error = e
                    continue
            else:
                # We failed all retries; log once and continue without augmentation
                if last_error is not None:
                    print(f"Augmentation failed for image {dataset_idx}: {last_error}. Using non-augmented sample.")

        # Ensure numpy arrays
        if isinstance(boxes, list):
            boxes = np.array(boxes, dtype=float)
        if isinstance(categories, list):
            categories = np.array(categories, dtype=int)

        # At this point, it's OK if `boxes` is empty – models can handle images with no objects
        formatted_annotations = self.annotations_as_coco(
            image_id=dataset_idx, categories=categories, boxes=boxes)
        result = self.processor(
            images=image, annotations=formatted_annotations, return_tensors="pt")

        # Remove the batch dimension added by the processor
        result = {k: v[0] for k, v in result.items()}
        return result
    
    @staticmethod
    def annotations_as_coco(image_id, categories, boxes):
        annotations = []
        for category, bbox in zip(categories, boxes):
            x1, y1, x2, y2 = bbox
            formatted_annotation = {
                "image_id": image_id,
                "category_id": category,
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "iscrowd": 0,
                "area": (x2 - x1) * (y2 - y1),
            }
            annotations.append(formatted_annotation)
        return {
            "image_id": image_id,
            "annotations": annotations,
        }

# %% [markdown]
# Now you can combine the image and annotation transformations to use on a batch of examples:

# %%
# Recreate datasets with the updated class
pytorch_dataset_train = PyTorchDetectionDataset(
    ds_train, processor, transform=train_augmentation_and_transform)
pytorch_dataset_valid = PyTorchDetectionDataset(
    ds_valid, processor, transform=valid_transform)
pytorch_dataset_test = PyTorchDetectionDataset(
    ds_test, processor, transform=valid_transform)

# Test a few samples to ensure they work
print("Testing individual samples...")
for i in [0, 15, 100]:  # Include sample 15 which had no boxes
    try:
        sample = pytorch_dataset_train[i]
        labels = sample.get('labels', {})
        boxes = labels.get('boxes', [])
        print(f"Sample {i}: {len(boxes)} boxes")
    except Exception as e:
        print(f"Error in sample {i}: {e}")

pytorch_dataset_train[15]

# %%
# Validate the dataset
def validate_dataset(dataset, name, num_samples=10):
    """Validate a dataset by checking a few samples"""
    print(f"Validating {name} dataset...")
    errors = 0
    
    for i in range(min(num_samples, len(dataset))):
        try:
            sample = dataset[i]
            # Check if we have valid labels
            if len(sample.get('labels', {}).get('boxes', [])) == 0:
                print(f"Warning: Sample {i} has no bounding boxes")
            print(f"Sample {i}: OK")
        except Exception as e:
            print(f"Error in sample {i}: {e}")
            errors += 1
    
    print(f"Validation complete. {errors} errors found in {num_samples} samples.")
    return errors == 0

# Validate datasets
validate_dataset(pytorch_dataset_train, "Training", 20)
validate_dataset(pytorch_dataset_valid, "Validation", 10)

# %% [markdown]
# You have successfully augmented the images and prepared their annotations. In the final step, create a custom collate_fn to batch images together.

# %%
def collate_fn(batch):
    data = {}
    data["pixel_values"] = torch.stack([x["pixel_values"] for x in batch])
    data["labels"] = [x["labels"] for x in batch]
    return data

# %% [markdown]
# ## Preparing function to compute mAP

# %%
id2label = {id: label for id, label in enumerate(ds_train.classes)}
label2id = {label: id for id, label in enumerate(ds_train.classes)}


@dataclass
class ModelOutput:
    logits: torch.Tensor
    pred_boxes: torch.Tensor


class MAPEvaluator:

    def __init__(self, image_processor, threshold=0.00, id2label=None):
        self.image_processor = image_processor
        self.threshold = threshold
        self.id2label = id2label

    def collect_image_sizes(self, targets):
        """Collect image sizes across the dataset as list of tensors with shape [batch_size, 2]."""
        image_sizes = []
        for batch in targets:
            batch_image_sizes = torch.tensor(np.array([x["size"] for x in batch]))
            image_sizes.append(batch_image_sizes)
        return image_sizes

    def collect_targets(self, targets, image_sizes):
        post_processed_targets = []
        for target_batch, image_size_batch in zip(targets, image_sizes):
            for target, (height, width) in zip(target_batch, image_size_batch):
                boxes = target["boxes"]
                boxes = sv.xcycwh_to_xyxy(boxes)
                boxes = boxes * np.array([width, height, width, height])
                boxes = torch.tensor(boxes)
                labels = torch.tensor(target["class_labels"])
                post_processed_targets.append({"boxes": boxes, "labels": labels})
        return post_processed_targets

    def collect_predictions(self, predictions, image_sizes):
        post_processed_predictions = []
        for batch, target_sizes in zip(predictions, image_sizes):
            batch_logits, batch_boxes = batch[1], batch[2]
            output = ModelOutput(logits=torch.tensor(batch_logits), pred_boxes=torch.tensor(batch_boxes))
            post_processed_output = self.image_processor.post_process_object_detection(
                output, threshold=self.threshold, target_sizes=target_sizes
            )
            post_processed_predictions.extend(post_processed_output)
        return post_processed_predictions

    @torch.no_grad()
    def __call__(self, evaluation_results):

        predictions, targets = evaluation_results.predictions, evaluation_results.label_ids

        image_sizes = self.collect_image_sizes(targets)
        post_processed_targets = self.collect_targets(targets, image_sizes)
        post_processed_predictions = self.collect_predictions(predictions, image_sizes)

        evaluator = MeanAveragePrecision(box_format="xyxy", class_metrics=True)
        evaluator.warn_on_many_detections = False
        evaluator.update(post_processed_predictions, post_processed_targets)

        metrics = evaluator.compute()

        # Replace list of per class metrics with separate metric for each class
        classes = metrics.pop("classes")
        map_per_class = metrics.pop("map_per_class")
        mar_100_per_class = metrics.pop("mar_100_per_class")
        for class_id, class_map, class_mar in zip(classes, map_per_class, mar_100_per_class):
            class_name = id2label[class_id.item()] if id2label is not None else class_id.item()
            metrics[f"map_{class_name}"] = class_map
            metrics[f"mar_100_{class_name}"] = class_mar

        metrics = {k: round(v.item(), 4) for k, v in metrics.items()}

        return metrics

eval_compute_metrics_fn = MAPEvaluator(image_processor=processor, threshold=0.01, id2label=id2label)

# %% [markdown]
# ## Training the detection model
# 
# You have done most of the heavy lifting in the previous sections, so now you are ready to train your model! The images in this dataset are still quite large, even after resizing. This means that finetuning this model will require at least one GPU.
# 
# Training involves the following steps:
# 
# - Load the model with [`AutoModelForObjectDetection`](https://huggingface.co/docs/transformers/main/en/model_doc/auto#transformers.AutoModelForObjectDetection) using the same checkpoint as in the preprocessing.
# - Define your training hyperparameters in [`TrainingArguments`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.TrainingArguments).
# - Pass the training arguments to [`Trainer`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.Trainer) along with the model, dataset, image processor, and data collator.
# - Call [`train()`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.Trainer.train) to finetune your model.
# 
# When loading the model from the same checkpoint that you used for the preprocessing, remember to pass the `label2id` and `id2label` maps that you created earlier from the dataset's metadata. Additionally, we specify `ignore_mismatched_sizes=True` to replace the existing classification head with a new one.

# %%
model = AutoModelForObjectDetection.from_pretrained(
    CHECKPOINT,
    id2label=id2label,
    label2id=label2id,
    num_labels=len(id2label),
    anchor_image_size=None,
    ignore_mismatched_sizes=True,
)

# %% [markdown]
# In the [`TrainingArguments`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.TrainingArguments) use `output_dir` to specify where to save your model, then configure hyperparameters as you see fit. For `num_train_epochs=10` training will take about 15 minutes in Google Colab T4 GPU, increase the number of epoch to get better results.
# 
# Important notes:
# 
# - Do not remove unused columns because this will drop the image column. Without the image column, you can't create `pixel_values`. For this reason, set `remove_unused_columns` to `False`.
# - Set `eval_do_concat_batches=False` to get proper evaluation results. Images have different number of target boxes, if batches are concatenated we will not be able to determine which boxes belongs to particular image.

# %%
training_args = TrainingArguments(
    output_dir=f"{dataset.name.replace(' ', '-')}-finetune",
    num_train_epochs=20,
    max_grad_norm=0.1,
    learning_rate=5e-5,
    warmup_steps=300,
    per_device_train_batch_size=12,  # Reduced batch size to be safer
    dataloader_num_workers=0,  # Use single process to avoid multiprocessing issues
    dataloader_pin_memory=False,  # Avoid pinning on CPU/limited GPU setups
    dataloader_drop_last=False,
    dataloader_persistent_workers=False,
    metric_for_best_model="eval_map",
    greater_is_better=True,
    load_best_model_at_end=True,
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=2,
    remove_unused_columns=False,
    eval_do_concat_batches=False,
    logging_steps=50,  # Add logging to monitor progress
)

# %% [markdown]
# Finally, bring everything together, and call [`train()`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.Trainer.train):

# %%
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=pytorch_dataset_train,
    eval_dataset=pytorch_dataset_valid,
    processing_class=processor,
    data_collator=collate_fn,
    compute_metrics=eval_compute_metrics_fn,
)

trainer.train()

# %% [markdown]
# ## Evaluate

# %%
# @title Collect predictions

targets = []
predictions = []

for i in range(len(ds_test)):
    path, source_image, annotations = ds_test[i]

    image = Image.open(path)
    inputs = processor(image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)

    w, h = image.size
    results = processor.post_process_object_detection(
        outputs, target_sizes=[(h, w)], threshold=0.3)

    detections = sv.Detections.from_transformers(results[0])

    targets.append(annotations)
    predictions.append(detections)

# %%
# @title Calculate mAP
mean_average_precision = sv.MeanAveragePrecision.from_detections(
    predictions=predictions,
    targets=targets,
)

print(f"map50_95: {mean_average_precision.map50_95:.2f}")
print(f"map50: {mean_average_precision.map50:.2f}")
print(f"map75: {mean_average_precision.map75:.2f}")

# %%
# @title Calculate Confusion Matrix
confusion_matrix = sv.ConfusionMatrix.from_detections(
    predictions=predictions,
    targets=targets,
    classes=ds_test.classes
)

_ = confusion_matrix.plot()

# %% [markdown]
# ## Save fine-tuned model on hard drive

# %%
model.save_pretrained("./rt-detr-rust/")
processor.save_pretrained("./rt-detr-rust/")

# %% [markdown]
# ## Inference with fine-tuned RT-DETR model

# %%
IMAGE_COUNT = 5

for i in range(IMAGE_COUNT):
    path, source_image, annotations = ds_test[i]

    image = Image.open(path)
    inputs = processor(image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)

    w, h = image.size
    results = processor.post_process_object_detection(
        outputs, target_sizes=[(h, w)], threshold=0.3)

    detections = sv.Detections.from_transformers(results[0]).with_nms(threshold=0.1)

    annotated_images = [
        annotate(source_image, annotations, ds_train.classes),
        annotate(source_image, detections, ds_train.classes)
    ]
    grid = sv.create_tiles(
        annotated_images,
        titles=['ground truth', 'prediction'],
        titles_scale=0.5,
        single_tile_size=(400, 400),
        tile_padding_color=sv.Color.WHITE,
        tile_margin_color=sv.Color.WHITE
    )
    sv.plot_image(grid, size=(6, 6))

# %%
import glob
from PIL import Image

import matplotlib.pyplot as plt

# Directory containing images
image_dir = "rust/"
image_paths = glob.glob(f"{image_dir}/*.jpg")

for img_path in image_paths:
    image = Image.open(img_path)
    inputs = processor(image, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)

    w, h = image.size
    results = processor.post_process_object_detection(
        outputs, target_sizes=[(h, w)], threshold=0.3)

    detections = sv.Detections.from_transformers(results[0]).with_nms(threshold=0.1)

    # Display annotated image
    annotated_image = image.copy()
    annotated_image = sv.BoxAnnotator().annotate(annotated_image, detections)
    labels = [
        model.config.id2label[class_id]
        for class_id in detections.class_id
    ]
    annotated_image = sv.LabelAnnotator().annotate(annotated_image, detections, labels=labels)
    annotated_image.thumbnail((600, 600))

    plt.figure(figsize=(6, 6))
    plt.imshow(annotated_image)
    plt.title(f"Predictions: {img_path}")
    plt.axis('off')
    plt.show()


