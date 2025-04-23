from transformers import CLIPModel, CLIPProcessor

# these two calls will download & cache the weights on first run
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
