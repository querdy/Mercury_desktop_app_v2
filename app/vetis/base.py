import json
import httpx
from typing import Optional, Any, Dict

from loguru import logger


class BaseSession:
    def __init__(self):
        self.client = httpx.Client(follow_redirects=True)
        self.cookies_file = 'cookies.json'

    def fetch(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> httpx.Response:
        if data:
            response = self.client.post(url, data=data, **kwargs)
        else:
            response = self.client.get(url, **kwargs)
        return response

    def save_cookies(self) -> None:
        with open(self.cookies_file, 'w') as file:
            cookies_dict = []
            for cookie in self.client.cookies.jar:
                cookies_dict.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                })
            json.dump(cookies_dict, file)
        logger.info("Cookies saved successfully.")

    def read_cookies(self) -> None:
        try:
            with open(self.cookies_file, 'r') as file:
                cookies_dict = json.load(file)
                for cookie in cookies_dict:
                    self.client.cookies.set(
                        cookie['name'],
                        cookie['value'],
                        domain=cookie['domain'],
                        path=cookie['path']
                    )
            logger.info("Cookies read successfully.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to read cookies: {e}")

    def clear_cookies(self) -> None:
        self.client.cookies.clear()
        logger.info("Cookies cleared.")

    def close(self) -> None:
        self.client.close()
        logger.info("HTTP client closed.")