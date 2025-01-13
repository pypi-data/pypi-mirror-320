# image_processing.py
from PIL import Image
import pytesseract
import pyzbar.pyzbar as pyzbar

def extract_text_from_image(image_path: str):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def decode_qr_code(image_path: str):
    image = Image.open(image_path)
    decoded_objects = pyzbar.decode(image)
    return [obj.data.decode('utf-8') for obj in decoded_objects]
