import os
import re
import time
from typing import List

import aiofiles
import httpx


class ImageGenerator:
    def __init__(
        self,
        auth_cookie_u: str,
        auth_cookie_srchhpgusr: str,
        logging_enabled: bool = True,
    ):
        self.client: httpx.Client = httpx.Client(
            cookies={"_U": auth_cookie_u, "SRCHHPGUSR": auth_cookie_srchhpgusr}
        )

        self.logging_enabled = logging_enabled

    def __log(self, message: str):
        if self.logging_enabled:
            print(message)

    def generate(self, prompt: str, num_images: int) -> list:
        images = []
        cycle = 0
        start = time.time()

        while len(images) < num_images:
            cycle += 1

            response = self.client.post(
                url=f"https://www.bing.com/images/create?q={prompt}&rt=3&FORM=GENCRE",
                data={"q": prompt, "qs": "ds"},
                follow_redirects=False,
                timeout=200,
            )

            if response.status_code != 302:
                raise Exception("🛑 Request to https://bing.com/ failed! (Redirect)")

            self.__log(f"✅ Request to https://bing.com/ sent! (cycle: {cycle})")

            if "being reviewed" in response.text or "has been blocked" in response.text:
                raise Exception("🛑 Prompt is being reviewed or blocked!")
            if "image creator in more languages" in response.text:
                raise Exception("🛑 Language is not supported by Bing yet!")

            result_id = (
                response.headers["Location"].replace("&nfy=1", "").split("id=")[-1]
            )
            results_url = f"https://www.bing.com/images/create/async/results/{result_id}?q={prompt}"

            self.__log(f"🕗 Awaiting generation... (cycle: {cycle})")
            start_time = time.time()
            while True:
                response = self.client.get(results_url)

                if time.time() - start_time > 200:
                    raise Exception("🛑 Waiting for results timed out!")

                if response.status_code != 200:
                    raise Exception(
                        "🛑 Exception happened while waiting for image generation! (NoResults)"
                    )

                if not response.text or response.text.find("errorMessage") != -1:
                    time.sleep(1)
                    continue
                else:
                    break

            new_images = [
                "https://tse" + link.split("?w=")[0]
                for link in re.findall('src="https://tse([^"]+)"', response.text)
            ]
            if len(new_images) == 0:
                raise Exception(
                    "🛑 No new images were generated for this cycle, please check your prompt"
                )
            images += new_images
            self.__log(
                f"✅ Successfully finished cycle {cycle} in {round(time.time() - start_time, 2)} seconds"
            )

        self.__log(
            f"✅ Finished generating {num_images} images in {round(time.time() - start, 2)} seconds and {cycle} cycles"
        )
        return images[:num_images]

    def save(self, images: list, output_dir: str) -> None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for images in images:
            response = self.client.get(images)
            if response.status_code != 200:
                raise Exception(
                    "🛑 Exception happened while saving image! (Response was not ok)"
                )

            filename = f"{images.split('/id/')[1]}.jpeg"
            with open(os.path.join(output_dir, filename), "wb") as f:
                f.write(response.content)
                f.close()

            self.__log(f"✅ Saved image {filename}!")


class AsyncImageGenerator:
    def __init__(
        self,
        auth_cookie_u: str,
        auth_cookie_srchhpgusr: str,
        logging_enabled: bool = True,
    ):
        self.client: httpx.AsyncClient = httpx.AsyncClient(
            cookies={"_U": auth_cookie_u, "SRCHHPGUSR": auth_cookie_srchhpgusr}
        )
        self.logging_enabled = logging_enabled

    def __log(self, message: str):
        if self.logging_enabled:
            print(message)

    async def generate(
        self, prompt: str, num_images: int, max_cycles: int = 4
    ) -> List[str]:
        images = []
        cycle = 0
        start = time.time()

        while len(images) < num_images and cycle < max_cycles:
            cycle += 1

            response = await self.client.post(
                url=f"https://www.bing.com/images/create?q={prompt}&rt=3&FORM=GENCRE",
                data={"q": prompt, "qs": "ds"},
                follow_redirects=False,
                timeout=200,
            )

            if response.status_code != 302:
                raise Exception("🛑 Request to https://bing.com/ failed! (Redirect)")

            self.__log(f"✅ Request to https://bing.com/ sent! (cycle: {cycle})")

            if "being reviewed" in response.text or "has been blocked" in response.text:
                raise Exception("🛑 Prompt is being reviewed or blocked!")
            if "image creator in more languages" in response.text:
                raise Exception("🛑 Language is not supported by Bing yet!")

            result_id = (
                response.headers["Location"].replace("&nfy=1", "").split("id=")[-1]
            )
            results_url = f"https://www.bing.com/images/create/async/results/{result_id}?q={prompt}"

            self.__log(f"🕗 Awaiting generation... (cycle: {cycle})")
            start_time = time.time()
            while True:
                response = await self.client.get(results_url)

                if time.time() - start_time > 200:
                    raise Exception("🛑 Waiting for results timed out!")

                if response.status_code != 200:
                    raise Exception(
                        "🛑 Exception happened while waiting for image generation! (NoResults)"
                    )

                if not response.text or response.text.find("errorMessage") != -1:
                    time.sleep(1)
                    continue
                else:
                    break

            new_images = [
                "https://tse" + link.split("?w=")[0]
                for link in re.findall('src="https://tse([^"]+)"', response.text)
            ]
            if len(new_images) == 0:
                raise Exception(
                    "🛑 No new images were generated for this cycle, please check your prompt"
                )
            images.extend(new_images)
            self.__log(
                f"✅ Successfully finished cycle {cycle} in {round(time.time() - start_time, 2)} seconds"
            )

        self.__log(
            f"✅ Finished generating images in {round(time.time() - start, 2)} seconds and {cycle} cycles"
        )
        return images[:num_images]

    async def save(self, images: List[str], output_dir: str) -> None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for image_url in images:
            response = await self.client.get(image_url)
            if response.status_code != 200:
                raise Exception(
                    "🛑 Exception happened while saving image! (Response was not ok)"
                )

            filename = f"{image_url.split('/')[-1].split('?')[0]}.jpeg"
            async with aiofiles.open(os.path.join(output_dir, filename), "wb") as f:
                await f.write(response.content)

            self.__log(f"✅ Saved image {filename}!")
