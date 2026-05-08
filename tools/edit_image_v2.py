"""
edit_image_v2.py — NB2 Edit Only Tool
Substitui a tool edit_image anterior.
Remove GPT Image 2 Edit, trava resolução em 1K, adiciona num_images, thinking_level, safety_tolerance.
"""

import os
import aiohttp
import asyncio
from typing import Optional, Literal
from pydantic import BaseModel, Field

FAL_API_KEY = os.getenv("FAL_API_KEY")
FAL_BASE_URL = "https://queue.fal.run"


class EditImageInput(BaseModel):
    prompt: str = Field(..., description="Descrição da edição a ser feita na(s) imagem(ns)")
    image_urls: list[str] = Field(..., description="URLs das imagens a editar (NB2 suporta até 14)")
    num_images: int = Field(default=4, ge=1, le=4)
    aspect_ratio: Literal[
        "auto", "1:1", "3:2", "4:3", "16:9", "21:9",
        "2:3", "3:4", "4:5", "9:16", "4:1", "8:1",
        "1:4", "1:8", "5:4"
    ] = Field(default="1:1")
    thinking_level: Literal["minimal", "high"] = Field(default="high")
    safety_tolerance: Literal["1", "2", "3", "4", "5", "6"] = Field(default="6")
    system_prompt: str = Field(default="")
    seed: Optional[int] = Field(default=None)


async def edit_image_v2(params: EditImageInput) -> list[dict]:
    """
    Edita imagens usando EXCLUSIVAMENTE Nano Banana 2 Edit.
    Resolução FIXA em 1K. Sempre gera num_images variações.
    """
    
    payload = {
        "prompt": params.prompt,
        "image_urls": params.image_urls,
        "num_images": params.num_images,
        "aspect_ratio": params.aspect_ratio,
        "resolution": "1K",  # TRAVADO PERMANENTEMENTE
        "thinking_level": params.thinking_level,
        "safety_tolerance": params.safety_tolerance,
        "limit_generations": True,
    }
    
    if params.system_prompt:
        payload["system_prompt"] = params.system_prompt
    if params.seed is not None:
        payload["seed"] = params.seed
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FAL_BASE_URL}/fal-ai/nano-banana-2/edit",
            headers=headers,
            json=payload
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Fal.ai API error: {resp.status}")
            result = await resp.json()
        
        status_url = result.get("status_url")
        if not status_url:
            raise Exception("No status_url")
        
        for _ in range(120):
            async with session.get(status_url, headers=headers) as status_resp:
                status_data = await status_resp.json()
            if status_data.get("status") == "COMPLETED":
                break
            await asyncio.sleep(1)
        else:
            raise Exception("Edit timed out")
        
        images = status_data.get("result", {}).get("images", [])
        if not images:
            raise Exception("No images in result")
        
        return [
            {
                "url": img.get("url"),
                "width": img.get("width"),
                "height": img.get("height"),
                "seed": img.get("seed"),
            }
            for img in images
        ]


TOOL_DEFINITION = {
    "name": "edit_image_v2",
    "description": "Edita imagens existentes usando EXCLUSIVAMENTE Nano Banana 2 Edit. Resolução fixa 1K, 4 variações por padrão, thinking_level='high' para máxima fidelidade.",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Descrição da edição a ser feita."
            },
            "image_urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "URLs das imagens a editar (NB2 suporta até 14)."
            },
            "num_images": {
                "type": "integer",
                "default": 4
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["auto", "1:1", "3:2", "4:3", "16:9", "21:9", "2:3", "3:4", "4:5", "9:16", "4:1", "8:1", "1:4", "1:8", "5:4"],
                "default": "1:1"
            },
            "thinking_level": {
                "type": "string",
                "enum": ["minimal", "high"],
                "default": "high"
            },
            "safety_tolerance": {
                "type": "string",
                "enum": ["1", "2", "3", "4", "5", "6"],
                "default": "6"
            },
            "system_prompt": {
                "type": "string"
            },
            "seed": {
                "type": "integer"
            }
        },
        "required": ["prompt", "image_urls"]
    }
}
