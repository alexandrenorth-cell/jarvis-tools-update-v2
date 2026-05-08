# 🚀 Guia de Migração — James Seek v2

## Para quem vai aplicar as alterações no backend

---

## ⚡ PASSO 1: Desativar Tools Antigas

No arquivo de registro de tools do agente (ex: `tools/registry.py` ou `agent/tools.py`), **remova ou comente** as seguintes tools:

```python
# ❌ REMOVER:
# "generate_image"  # antiga, suportava GPT Image 2
# "edit_image"      # antiga, suportava GPT Image 2
```

---

## ⚡ PASSO 2: Adicionar Tools Novas

Copie os arquivos para o diretório de tools do projeto:

```bash
cp tools/generate_image_v2.py caminho/do/projeto/tools/
cp tools/edit_image_v2.py caminho/do/projeto/tools/
```

Registre as novas tools no agente:

```python
from tools.generate_image_v2 import generate_image_v2, TOOL_DEFINITION as GEN_DEF
from tools.edit_image_v2 import edit_image_v2, TOOL_DEFINITION as EDIT_DEF

# No dicionário de tools do agente:
TOOLS = {
    # ... outras tools ...
    "generate_image_v2": {
        "function": generate_image_v2,
        "definition": GEN_DEF,
    },
    "edit_image_v2": {
        "function": edit_image_v2,
        "definition": EDIT_DEF,
    },
}
```

---

## ⚡ PASSO 3: Atualizar System Prompt do Agente

No System Prompt do James, **substitua**:

```diff
- Use a ferramenta `generate_image` com quality="standard" ou "premium"
+ Use a ferramenta `generate_image_v2` (NB2 exclusivo, 4 variações, 1K)
```

Remova TODAS as menções ao GPT Image 2 e ao parâmetro `quality`.

**Trecho a remover do System Prompt:**
- `GPT Image 2`
- `quality="premium"`
- `resolution="2K"` ou `"4K"` (na ferramenta de geração)
- `enhance_prompt` e `enhance_intensity`

---

## ⚡ PASSO 4: Verificar Variáveis de Ambiente

As tools usam:

```bash
FAL_API_KEY=...  # Deve já existir no ambiente
```

**Nenhuma variável nova é necessária.** A API key do Fal.ai já está configurada.

---

## ⚡ PASSO 5: Testar

### Teste de Geração

```bash
python -c "
import asyncio
from tools.generate_image_v2 import generate_image_v2, GenerateImageInput

async def test():
    result = await generate_image_v2(GenerateImageInput(
        prompt='A black cat wearing sunglasses',
    ))
    print(f'✅ Geradas {len(result)} imagens (esperado: 4)')
    for i, img in enumerate(result):
        print(f'  [{i+1}] url={img[\"url\"][:60]}... seed={img[\"seed\"]}')

asyncio.run(test())
"
```

### Teste de Edição

```bash
python -c "
import asyncio
from tools.edit_image_v2 import edit_image_v2, EditImageInput

async def test():
    result = await edit_image_v2(EditImageInput(
        prompt='Make it black and white',
        image_urls=['https://example.com/photo.jpg'],
    ))
    print(f'✅ Editadas {len(result)} imagens (esperado: 4)')

asyncio.run(test())
"
```

---

## ✅ Checklist de Deploy

- [ ] Tools antigas (`generate_image`, `edit_image`) removidas/comentadas
- [ ] Novos arquivos copiados para o diretório `tools/`
- [ ] Tools registradas como `generate_image_v2` e `edit_image_v2`
- [ ] System Prompt atualizado (sem GPT Image 2, sem `quality`)
- [ ] Variável `FAL_API_KEY` OK
- [ ] Teste de geração passou (4 imagens, thinking_level=high)
- [ ] Teste de edição passou (4 imagens)
- [ ] Logs sem erros

---

## 🔄 Rollback (se necessário)

Reverta o commit ou recoloque as tools antigas no registro. As tools antigas continuam compatíveis com a API do Fal.ai.

```python
# Rollback rápido:
TOOLS = {
    "generate_image": { ... },  # volta a original
    "edit_image": { ... },      # volta a original
}
```

---

## 📞 Suporte

Dúvidas? **Falar com o Alê (Alexandre Martins)** — ele aprova ou reprova na hora! 🔥
