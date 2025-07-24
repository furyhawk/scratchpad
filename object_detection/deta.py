from transformers import AutoImageProcessor, DetaForObjectDetection
from PIL import Image
import requests
import torch
import os
import warnings

# Suppress CUDA extension warnings if they fail to compile
warnings.filterwarnings(
    "ignore",
    message="Could not load the custom kernel for multi-scale deformable attention",
)

# Set environment variables to handle CUDA compilation issues
os.environ["TORCH_CUDA_ARCH_LIST"] = "8.9"  # Adjust based on your GPU architecture
os.environ["FORCE_CUDA"] = "0"  # Force CPU-only mode to avoid CUDA issues

try:
    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)

    print("Loading image processor...")
    image_processor = AutoImageProcessor.from_pretrained("jozhang97/deta-swin-large")

    print(
        "Loading model (this may take a while and show warnings about CUDA extensions)..."
    )
    # Load model without device_map to avoid accelerate dependency issues
    model = DetaForObjectDetection.from_pretrained(
        "jozhang97/deta-swin-large",
        torch_dtype=torch.float32,
        disable_custom_kernels=True,
    )
    # Move model to CPU explicitly
    model = model.to("cpu")

    print("Processing image...")
    inputs = image_processor(images=image, return_tensors="pt")

    print("Running inference...")
    with torch.no_grad():
        outputs = model(**inputs)

    # convert outputs (bounding boxes and class logits) to Pascal VOC format (xmin, ymin, xmax, ymax)
    target_sizes = torch.tensor([image.size[::-1]])
    results = image_processor.post_process_object_detection(
        outputs, threshold=0.5, target_sizes=target_sizes
    )[0]

    print(f"\nDetected {len(results['scores'])} objects:")
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        box = [round(i, 2) for i in box.tolist()]
        print(
            f"Detected {model.config.id2label[label.item()]} with confidence "
            f"{round(score.item(), 3)} at location {box}"
        )

except Exception as e:
    print(f"Error occurred: {e}")
    print("\nTroubleshooting suggestions:")
    print("1. The CUDA extension compilation failed. This is often due to:")
    print("   - PyTorch/CUDA version mismatch")
    print("   - Missing or incompatible CUDA toolkit")
    print("   - Transformers version compatibility issues")
    print("\n2. Alternative solutions:")
    print("   - Use CPU-only inference (current approach)")
    print("   - Try a different model that doesn't require custom CUDA kernels")
    print("   - Use a container with pre-compiled extensions")
    print("   - Downgrade PyTorch to a compatible version")
