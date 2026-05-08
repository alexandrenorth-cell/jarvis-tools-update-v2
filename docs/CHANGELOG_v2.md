# 🔧 James Seek v2 — Changelog

## 📅 Data: 08/05/2026

---

## 🚀 O QUE MUDOU

### ✅ ADICIONADO

| Parâmetro | Tool | Tipo | Default | Descrição |
|-----------|------|------|---------|-----------|
| `num_images` | `generate_image_v2`, `edit_image_v2` | `int (1-4)` | `4` | Número de variações por chamada. Gera 4 imagens de uma vez. |
| `thinking_level` | `generate_image_v2`, `edit_image_v2` | `enum` | `"high"` | Controla o "raciocínio" do NB2. `"high"` = maior fidelidade para rostos, identidade, proporções. |
| `safety_tolerance` | `generate_image_v2`, `edit_image_v2` | `enum` | `"6"` | Tolerância de segurança. `"6"` = mínima chance de bloqueio falso. |
| `system_prompt` | `generate_image_v2`, `edit_image_v2` | `string` | `""` | System prompt opcional para estilo global consistente. |
| `enable_web_search` | `generate_image_v2` | `boolean` | `false` | Permite busca web para referências reais (+$0.015). |

### ❌ REMOVIDO

| Parâmetro | Motivo |
|-----------|--------|
| `quality` (`"standard"` / `"premium"`) | GPT Image 2 removido. Apenas NB2. |
| `resolution` (opções 2K, 4K) | Travado em 1K. Upscale via tool separada `upscale_image`. |
| `enhance_prompt` | Automatizado internamente. Não exposto ao agente. |
| `enhance_intensity` | Automatizado internamente. |

### 🔒 TRAVADO

| Parâmetro | Valor Fixo | Motivo |
|-----------|------------|--------|
| `resolution` | `"1K"` | Sob demanda de upscale separado |
| `limit_generations` | `true` | Evitar loops internos |

---

## 🎯 CONFIGURAÇÃO PADRÃO DEFINITIVA

```yaml
motor: Nano Banana 2 (exclusivo)
num_images: 4
resolution: 1K (travado)
thinking_level: high
safety_tolerance: "6"
system_prompt: "" (vazio)
enable_web_search: false
aspect_ratio: 1:1 (default, configurável)
```

---

## 🏷️ NOMES DAS TOOLS

- **Antiga:** `generate_image` → **Nova:** `generate_image_v2`
- **Antiga:** `edit_image` → **Nova:** `edit_image_v2`
- **Mantidas:** `upscale_image`, `remove_background`

---

## 🧪 TESTE RÁPIDO PÓS-DEPLOY

```python
# Teste 1: Geração com 4 variações
import asyncio
from tools.generate_image_v2 import generate_image_v2, GenerateImageInput

async def test():
    result = await generate_image_v2(GenerateImageInput(
        prompt="A red motorcycle on a mountain trail at sunset",
        # num_images=4 (default)
        # thinking_level="high" (default)
    ))
    assert len(result) == 4, f"Expected 4 images, got {len(result)}"
    print(f"✅ Teste geração: {len(result)} imagens geradas")

asyncio.run(test())

# Teste 2: Edição
async def test_edit():
    result = await edit_image_v2(EditImageInput(
        prompt="Add a blue helmet to the rider",
        image_urls=["https://example.com/photo.jpg"],
    ))
    assert len(result) == 4
    print(f"✅ Teste edição: {len(result)} imagens geradas")
```

---

## 📊 IMPACTO FINANCEIRO

| Cenário | Antes | Depois |
|---------|-------|--------|
| 1 imagem | $0.08 (NB2 1K) | $0.32 (4 imgs NB2 1K) |
| Upscale | $0.08 | $0.017 (SeedVR2) |
| Edição 4 vars | $0.32 (NB2 Edit 4×1K) | Igual |

**Custo médio por lote de 4 imagens: ~$0.32**
