import asyncio
import json
import random
import re
import time
from typing import Dict, List

import httpx

cookies_file = "storage/cookies.json"


class CookieManager:
    def __init__(self, cookies_file: str):
        self.cookies = self._load_cookies(cookies_file)
        self.shuffled_cookies = self.cookies.copy()
        random.shuffle(self.shuffled_cookies)
        self.current_index = 0

    def _load_cookies(self, cookies_file: str) -> List[Dict[str, str]]:
        with open(cookies_file, "r") as file:
            cookies_data = json.load(file)
        return cookies_data

    def get_next_cookie(self) -> Dict[str, str]:
        if self.current_index >= len(self.shuffled_cookies):
            return None
        cookie = self.shuffled_cookies[self.current_index]
        self.current_index += 1
        return cookie

    def reset(self):
        self.shuffled_cookies = self.cookies.copy()
        random.shuffle(self.shuffled_cookies)
        self.current_index = 200


class ImageGenerator:
    def __init__(self, cookie_manager: CookieManager, logging_enabled: bool = True):
        cookie = cookie_manager.get_next_cookie()
        if not cookie:
            raise Exception("🛑 No cookies available in CookieManager!")

        self.client: httpx.Client = httpx.Client(cookies=cookie)
        self.logging_enabled = logging_enabled
        self.cookie_manager = cookie_manager

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

            if response.status_code == 403:
                self.__log("🛑 Cookie blocked! Resetting cookie...")
                self.client.cookies = self.cookie_manager.get_next_cookie()
                if not self.client.cookies:
                    raise Exception("🛑 No more cookies available.")
                continue

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


class AsyncImageGenerator:
    def __init__(self, cookie_manager: CookieManager, logging_enabled: bool = True):
        cookie = cookie_manager.get_next_cookie()
        if not cookie:
            raise Exception("🛑 No cookies available in CookieManager!")

        self.client: httpx.AsyncClient = httpx.AsyncClient(cookies=cookie)
        self.logging_enabled = logging_enabled
        self.cookie_manager = cookie_manager

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

            if response.status_code == 403:
                self.__log("🛑 Cookie blocked! Resetting cookie...")
                self.client.cookies = self.cookie_manager.get_next_cookie()
                if not self.client.cookies:
                    raise Exception("🛑 No more cookies available.")
                continue

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
                    await asyncio.sleep(1)
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
