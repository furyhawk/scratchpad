"""
Alternative object detection script using DETR instead of DETA
DETR doesn't require custom CUDA kernels and should work more reliably
"""
from transformers import AutoImageProcessor, DetrForObjectDetection
from PIL import Image
import requests
import torch
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def detect_objects_detr(image_url=None, image_path=None, threshold=0.7):
    """
    Perform object detection using DETR model
    
    Args:
        image_url: URL to download image from
        image_path: Local path to image file
        threshold: Confidence threshold for detections
    """
    try:
        # Load image
        if image_url:
            print(f"Downloading image from: {image_url}")
            image = Image.open(requests.get(image_url, stream=True).raw)
        elif image_path:
            print(f"Loading image from: {image_path}")
            image = Image.open(image_path)
        else:
            raise ValueError("Either image_url or image_path must be provided")

        print("Loading DETR model...")
        # Use DETR which doesn't require custom CUDA kernels
        image_processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
        model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

        print("Processing image...")
        inputs = image_processor(images=image, return_tensors="pt")
        
        print("Running inference...")
        with torch.no_grad():
            outputs = model(**inputs)

        # Convert outputs to COCO detection format
        target_sizes = torch.tensor([image.size[::-1]])
        results = image_processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=threshold
        )[0]

        print(f"\nDetected {len(results['scores'])} objects:")
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            print(
                f"Detected {model.config.id2label[label.item()]} with confidence "
                f"{round(score.item(), 3)} at location {box}"
            )
            
        return results

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def detect_objects_yolos():
    """
    Alternative using YOLOS model (YOLO + Transformer)
    """
    try:
        from transformers import YolosImageProcessor, YolosForObjectDetection
        
        url = "http://images.cocodataset.org/val2017/000000039769.jpg"
        image = Image.open(requests.get(url, stream=True).raw)

        print("Loading YOLOS model...")
        image_processor = YolosImageProcessor.from_pretrained('hustvl/yolos-tiny')
        model = YolosForObjectDetection.from_pretrained('hustvl/yolos-tiny')

        inputs = image_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)

        target_sizes = torch.tensor([image.size[::-1]])
        results = image_processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.7
        )[0]

        print(f"\nYOLOS detected {len(results['scores'])} objects:")
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            print(
                f"Detected {model.config.id2label[label.item()]} with confidence "
                f"{round(score.item(), 3)} at location {box}"
            )
            
        return results

    except ImportError:
        print("YOLOS model not available in this transformers version")
        return None
    except Exception as e:
        print(f"Error with YOLOS: {e}")
        return None

if __name__ == "__main__":
    # Test with the same image as the original script
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    
    print("=== Testing DETR Model ===")
    results_detr = detect_objects_detr(image_url=url)
    
    print("\n=== Testing YOLOS Model ===")
    results_yolos = detect_objects_yolos()
    
    print("\n=== Summary ===")
    print("Alternative models that don't require custom CUDA kernels:")
    print("1. DETR (facebook/detr-resnet-50) - Reliable baseline")
    print("2. YOLOS (hustvl/yolos-tiny) - YOLO + Transformer hybrid")
    print("3. RT-DETR models - Real-time DETR variants")
    print("4. DINO models - Improved DETR variants")
