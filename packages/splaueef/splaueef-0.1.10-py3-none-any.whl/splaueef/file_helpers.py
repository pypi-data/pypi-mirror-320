# file_helpers.py
import os

async def save_file(file_content: bytes, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as file:
        file.write(file_content)

def read_file(path: str):
    with open(path, "rb") as file:
        return file.read()

def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)
