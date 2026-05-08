"""
generate_image_v2.py — NB2 Only Image Generation Tool
Substitui a tool generate_image anterior.
Remove GPT Image 2, trava resolução em 1K, adiciona num_images, thinking_level, safety_tolerance, system_prompt, enable_web_search.
"""

import os
import aiohttp
import asyncio
from typing import Optional, Literal
from pydantic import BaseModel, Field

FAL_API_KEY = os.getenv("FAL_API_KEY")
FAL_BASE_URL = "https://queue.fal.run"


class GenerateImageInput(BaseModel):
    prompt: str = Field(..., description="Prompt detalhado para geração da imagem")
    num_images: int = Field(
        default=4,
        ge=1,
        le=4,
        description="Número de imagens a gerar. PADRÃO FIXO: 4. Máximo NB2: 4."
    )
    aspect_ratio: Literal[
        "auto", "1:1", "3:2", "4:3", "16:9", "21:9",
        "2:3", "3:4", "4:5", "9:16", "4:1", "8:1",
        "1:4", "1:8", "5:4"
    ] = Field(
        default="1:1",
        description="Aspect ratio da imagem gerada"
    )
    thinking_level: Literal["minimal", "high"] = Field(
        default="high",
        description="Nível de pensamento do modelo. 'high' = MAIOR FIDELIDADE para rostos, identidade, proporções."
    )
    safety_tolerance: Literal["1", "2", "3", "4", "5", "6"] = Field(
        default="6",
        description="Tolerância de segurança. '6' = menor chance de bloqueio falso."
    )
    system_prompt: str = Field(
        default="",
        description="System prompt opcional para guiar o estilo global das gerações"
    )
    enable_web_search: bool = Field(
        default=False,
        description="Permite busca web para referências reais. Custa +$0.015/geração."
    )
    seed: Optional[int] = Field(
        default=None,
        description="Seed para reprodutibilidade (opcional)"
    )


async def generate_image_v2(params: GenerateImageInput) -> list[dict]:
    """
    Gera imagens usando EXCLUSIVAMENTE Nano Banana 2 (Gemini Flash).
    Resolução FIXA em 1K. Sempre gera num_images variações.
    """
    
    payload = {
        "prompt": params.prompt,
        "num_images": params.num_images,
        "aspect_ratio": params.aspect_ratio,
        "resolution": "1K",  # TRAVADO PERMANENTEMENTE
        "thinking_level": params.thinking_level,
        "safety_tolerance": params.safety_tolerance,
        "limit_generations": True,
    }
    
    if params.system_prompt:
        payload["system_prompt"] = params.system_prompt
    
    if params.enable_web_search:
        payload["enable_web_search"] = True
    
    if params.seed is not None:
        payload["seed"] = params.seed
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FAL_BASE_URL}/fal-ai/nano-banana-2",
            headers=headers,
            json=payload
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Fal.ai API error: {resp.status}")
            result = await resp.json()
        
        status_url = result.get("status_url")
        if not status_url:
            raise Exception("No status_url in response")
        
        for _ in range(120):
            async with session.get(status_url, headers=headers) as status_resp:
                status_data = await status_resp.json()
            
            if status_data.get("status") == "COMPLETED":
                break
            await asyncio.sleep(1)
        else:
            raise Exception("Generation timed out")
        
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
    "name": "generate_image_v2",
    "description": "Gera imagens com IA usando EXCLUSIVAMENTE Nano Banana 2 (Gemini Flash). Resolução fixa 1K, 4 variações por padrão, thinking_level='high' para máxima fidelidade.",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Descrição detalhada da imagem a ser gerada."
            },
            "num_images": {
                "type": "integer",
                "description": "Número de imagens (1-4). Padrão: 4.",
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
                "type": "string",
                "description": "System prompt opcional para estilo global."
            },
            "enable_web_search": {
                "type": "boolean",
                "default": false
            },
            "seed": {
                "type": "integer",
                "description": "Seed para reprodutibilidade (opcional)."
            }
        },
        "required": ["prompt"]
    }
}
