from __future__ import annotations

import argparse
import logging
import os
import warnings
from typing import Any, Dict, Iterable, Tuple

import requests
import torch
from PIL import Image
from transformers import AutoImageProcessor, DetaForObjectDetection


# ------------------------------
# Configuration & logging
# ------------------------------

# Suppress CUDA extension warnings if they fail to compile
warnings.filterwarnings(
    "ignore",
    message="Could not load the custom kernel for multi-scale deformable attention",
)
# Suppress the assign parameter warnings for state dict loading
warnings.filterwarnings(
    "ignore",
    message=".*copying from a non-meta parameter.*assign=True.*",
    category=UserWarning,
)

# Set environment variables to handle CUDA compilation issues
os.environ["TORCH_CUDA_ARCH_LIST"] = os.environ.get("TORCH_CUDA_ARCH_LIST", "8.9")
# os.environ["FORCE_CUDA"] = "0"  # Force CPU-only mode to avoid CUDA issues

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ------------------------------
# Small helpers
# ------------------------------

DEFAULT_IMAGE_URL = "http://images.cocodataset.org/val2017/000000039769.jpg"


def load_image(url: str) -> Image.Image:
    """Load an image from a URL using requests streaming.

    Raises requests.HTTPError on network failures.
    """
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    return Image.open(resp.raw).convert("RGB")


def load_model_and_processor(preference: str = "auto") -> Tuple[Any, Any]:
    """Load a DETR model first (stable), falling back to DETA if needed.

    preference:
      - "detr": try DETR only, error if it fails
      - "deta": try DETA only, error if it fails
      - "auto": try DETR, then fallback to DETA
    Returns (model, image_processor)
    """
    preference = preference.lower()

    def _load_detr() -> Tuple[Any, Any]:
        logger.info("Loading DETR model...")
        from transformers import DetrForObjectDetection

        model = DetrForObjectDetection.from_pretrained(
            "facebook/detr-resnet-50", torch_dtype=torch.float32
        )
        processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
        logger.info("Successfully loaded DETR model")
        return model, processor

    def _load_deta() -> Tuple[Any, Any]:
        logger.info("Loading DETA model...")
        model = DetaForObjectDetection.from_pretrained(
            "nielsr/deta-resnet-50",
            torch_dtype=torch.float32,
            force_download=False,
            local_files_only=False,
            ignore_mismatched_sizes=True,
        )
        processor = AutoImageProcessor.from_pretrained("nielsr/deta-resnet-50")
        logger.info("Successfully loaded DETA model")
        return model, processor

    if preference == "detr":
        return _load_detr()
    if preference == "deta":
        return _load_deta()

    # auto: try DETR then DETA
    try:
        return _load_detr()
    except Exception as detr_error:  # noqa: BLE001 - preserve broad fallback behavior
        logger.info(f"DETR model failed: {detr_error}")
        logger.info("Trying DETA model as fallback...")
        try:
            return _load_deta()
        except Exception as deta_error:  # noqa: BLE001 - preserve broad fallback behavior
            logger.error(f"Both models failed. DETA error: {deta_error}")
            raise RuntimeError("Unable to load any model") from deta_error


def run_inference(
    image: Image.Image, model: Any, processor: Any, threshold: float = 0.5
) -> Dict[str, Iterable[Any]]:
    """Run forward pass and post-process to object detections dict.

    Returns a dict with keys: 'scores', 'labels', 'boxes'.
    """
    logger.info("Processing image...")
    inputs = processor(images=image, return_tensors="pt")

    logger.info("Running inference...")
    with torch.no_grad():
        outputs = model(**inputs)

    # convert outputs (bounding boxes and class logits) to Pascal VOC format
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(
        outputs, threshold=threshold, target_sizes=target_sizes
    )[0]
    return results


def print_detections(results: Dict[str, Iterable[Any]], model: Any) -> None:
    logger.info(f"\nDetected {len(results['scores'])} objects:")
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        box = [round(i, 2) for i in box.tolist()]
        logger.info(
            "Detected %s with confidence %s at location %s",
            model.config.id2label[label.item()],
            round(score.item(), 3),
            box,
        )


def _troubleshooting_note() -> str:
    return (
        "\nTroubleshooting suggestions:\n"
        "1. The CUDA extension compilation failed. This is often due to:\n"
        "   - PyTorch/CUDA version mismatch\n"
        "   - Missing or incompatible CUDA toolkit\n"
        "   - Transformers version compatibility issues\n\n"
        "2. Alternative solutions:\n"
        "   - Use CPU-only inference (current approach)\n"
        "   - Try a different model that doesn't require custom CUDA kernels\n"
        "   - Use a container with pre-compiled extensions\n"
        "   - Downgrade PyTorch to a compatible version"
    )


def main(
    url: str = DEFAULT_IMAGE_URL,
    threshold: float = 0.5,
    model_pref: str = "auto",
) -> None:
    try:
        logger.info("Loading image processor...")
        # Initial processor fetch (will be overwritten by chosen model's processor)
        _ = AutoImageProcessor.from_pretrained("nielsr/deta-resnet-50")

        logger.info(
            "Loading model (this may take a while and show warnings about CUDA extensions)..."
        )
        model, processor = load_model_and_processor(preference=model_pref)

        image = load_image(url)
        results = run_inference(image=image, model=model, processor=processor, threshold=threshold)
        print_detections(results, model)
    except Exception as e:  # noqa: BLE001 - keep broad to surface guidance
        logger.error("Error occurred: %s", e)
        logger.error(_troubleshooting_note())


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simple DETR/DETA object detection runner")
    p.add_argument(
        "--url",
        default=DEFAULT_IMAGE_URL,
        help="Image URL to run detection on (default: COCO sample)",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Score threshold for detections (default: 0.5)",
    )
    p.add_argument(
        "--model",
        choices=["auto", "detr", "deta"],
        default="auto",
        help="Model preference: try DETR, DETA, or auto fallback (default)",
    )
    return p


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    main(url=args.url, threshold=args.threshold, model_pref=args.model)
