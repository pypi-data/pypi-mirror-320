# api_helpers.py
import aiohttp

async def get(url: str, params: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()

async def post(url: str, data: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
