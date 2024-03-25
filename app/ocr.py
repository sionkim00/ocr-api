import pathlib

import pytesseract
from PIL import Image

BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
img_path = IMG_DIR / "test_image2.png"

img = Image.open(img_path)

ocr_prediction = pytesseract.image_to_string(img)
ocr_predictions = [x for x in ocr_prediction.split("\n")]
print(ocr_predictions)
