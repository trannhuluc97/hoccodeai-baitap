# pip install pillow diffusers torchvision torch accelerate

from diffusers import DiffusionPipeline, EulerDiscreteScheduler
import torch

def generate_image(prompt, width, height, steps=30):
    # Load the pipeline
    pipeline = DiffusionPipeline.from_pretrained("stablediffusionapi/anything-v5",
                                                 use_safetensors=True, safety_checker=None, requires_safety_checker=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipeline.to(device)

    pipeline.scheduler = EulerDiscreteScheduler.from_config(pipeline.scheduler.config)

    image = pipeline(prompt, width=width, height=height, num_inference_steps=steps).images[0]

    filename = f"{prompt.replace(' ', '_')}.png"
    image.save(filename)
    print(f"Image saved as {filename}")

if __name__ == "__main__":
    prompt = input("Enter the prompt for the image: ")
    width = int(input("Enter the horizontal size of the image: "))
    height = int(input("Enter the vertical size of the image: "))

    generate_image(prompt, width, height)