import torch
from PIL import Image
import open_clip

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-H-14-quickgelu", pretrained="dfn5b"
)
model.eval()  # model in train mode by default, impacts some models with BatchNorm or stochastic depth active
tokenizer = open_clip.get_tokenizer("ViT-H-14-quickgelu")

image = preprocess(Image.open("../asserts/inkpunk.png")).unsqueeze(0)
text = tokenizer(["a diagram", "a dog", "a cat"])

with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)

print("Label probs:", text_probs)  # prints: [[1., 0., 0.]]
