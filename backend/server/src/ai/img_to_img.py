from __future__ import annotations

import base64
import logging
import os
from typing import Literal, Optional

import dotenv
from openai import OpenAI

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv("./.env.local")

class ImgToImg:
    """Class to generate image(s) from image(s).

    Limitations:
    * Latency: Complex prompts may take up to 2 minutes to process.
    * Text Rendering: Although significantly improved over the DALL·E series,
        the model can still struggle with precise text placement and clarity.
    * Consistency: While capable of producing consistent imagery,
        the model may occasionally struggle to maintain visual consistency
        for recurring characters or brand elements across multiple generations.
    * Composition Control: Despite improved instruction following,
        the model may have difficulty placing elements precisely in structured
        or layout-sensitive compositions.
    """

    client: OpenAI
    model_name: str

    def __init__(
            self,
            model_name: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        """Initialize instance."""
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or os.getenv("OPENAI_MODEL_NAME")
        self.client = OpenAI(api_key=api_key)

        logger.info("Client initialized with model: %s", self.model_name)

    def generate(
            self,
            reference_img_list: list[bytes],
            size: Optional[Literal["1024x1024", "1536x1024", "1024x1536", "auto"]] = "1024x1024",
            quality: Optional[Literal["low", "medium", "high", "auto"]] = "low",
    ) -> list[bytes]:
        """Generate image(s) based on image(s)."""
        prompt = "Generate a composite image based on the attached images."
        result = self.client.images.edit(
            model=self.model_name,
            prompt=prompt,
            image=reference_img_list,
            size=size,
            quality=quality,
        )

        logger.info("result: %s", result)

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        return [image_bytes]

