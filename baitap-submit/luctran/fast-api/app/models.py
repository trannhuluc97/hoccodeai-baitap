from pydantic import BaseModel
from typing import Optional

class ImageRequest(BaseModel):
    prompt: str
    num_inference_steps: Optional[int] = 25
    guidance_scale: Optional[float] = 7.5
    width: Optional[int] = 512
    height: Optional[int] = 512
    negative_prompt: Optional[str] = "low quality, lowres, wrong anatomy, bad anatomy, deformed, disfigured, ugly"

class APIResponse(BaseModel):
    image: str # base64 of image