import torch

from models import ImageRequest
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL.Image import Image

pipeline = StableDiffusionPipeline.from_pretrained(
    "sd-legacy/stable-diffusion-v1-5",
    torch_dtype=torch.float16,  # Nếu máy của bạn không có GPU thì bỏ dòng này nha
    use_safetensors=True,
)
pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
    pipeline.scheduler.config)

device = "cuda" if torch.cuda.is_available() else "cpu"
# MPS chỉ có trên macOS dòng M1 trở đi
device = 'mps' if torch.backends.mps.is_available() else device
pipeline.to(device)

async def generate_image(imgRequest: ImageRequest) -> Image:
    image: Image = pipeline(
        prompt=imgRequest.prompt,
        negative_prompt=imgRequest.negative_prompt,
        width=imgRequest.width,
        height=imgRequest.height,
        guidance_scale=imgRequest.guidance_scale,
        num_inference_steps=imgRequest.num_inference_steps,
    ).images[0]
    return image
