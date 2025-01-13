# Gen Bing

A Python library for generating and saving images using Bing's Image Creator.

## Installation PyPi

```bash
pip3 install -U --no-cache-dir gen-bing
```

## Usage Async

```python
from Bing import AsyncImageGenerator

async def main():
    GEN = AsyncImageGenerator()
    images = await GEN.generate(prompt="A cute cat is playing on a bed. Digital Art 3D.", num_images=4)
    await GEN.save(images, output_dir="images/")

import asyncio
asyncio.run(main())
```

## Usage Sync

```python
from Bing import ImageGenerator

GEN = ImageGenerator()
images = GEN.generate(prompt="A cute cat is playing on a bed. Digital Art 3D.", num_images=4)
GEN.save(images, output_dir="images/")
```

## DON'T TRY THIS AT HOME 🏡 🙏🏻

## LuciferReborns