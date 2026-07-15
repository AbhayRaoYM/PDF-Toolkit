import os
import img2pdf
from PIL import Image


def convert(image_paths: list, output_path: str) -> str:
    """Combine a list of image files into a single PDF."""
    # Ensure all images are in a format img2pdf accepts (convert if needed)
    processed = []
    for path in image_paths:
        img = Image.open(path)
        # Convert palette/RGBA modes to RGB for PDF compatibility
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
            rgb_path = path + "_converted.jpg"
            img.save(rgb_path, "JPEG")
            processed.append(rgb_path)
        else:
            processed.append(path)

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(processed))

    # Clean up any converted temp files
    for path in processed:
        if path.endswith("_converted.jpg") and os.path.isfile(path):
            os.remove(path)

    return output_path
