from PIL import Image


def image_summary(file_path):
    image = Image.open(file_path)
    width, height = image.size
    return {
        "width": width,
        "height": height,
        "mode": image.mode,
        "format": image.format or "Unknown",
        "description": "Image loaded successfully. This app can inspect dimensions and format. Add OCR or vision models for deeper reading.",
    }
