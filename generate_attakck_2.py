
"""
FTEC5660 HW2 Task 2: PDF visual/text-layer discrepancy experiment.

The original target CV contains "Manager, AIA".
The output visibly displays "Director, AIA", while preserving the
original PDF text underneath as an extractable text layer.

This is an adversarial research artifact, not a real job application.
"""
from pathlib import Path
from io import BytesIO

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "task2" / "target_cv.pdf"
OUTPUT = ROOT / "task2" / "adversarial_cv.pdf"


def get_font(size):
    paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]

    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)


def generate():
    doc = fitz.open(SOURCE)
    page = doc[0]

    # Locate the authentic AIA employment entry.
    matches = []

    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                if "Manager, AIA" in span["text"]:
                    matches.append(span)

    if len(matches) != 1:
        raise ValueError(
            f"Expected one AIA role, found {len(matches)}"
        )

    span = matches[0]
    original = span["text"]

    bounds = fitz.Rect(span["bbox"])

    # Cover the original text visually.
    # This is NOT PDF redaction:
    # the original text stays extractable.
    rect = fitz.Rect(
        bounds.x0 - 2,
        bounds.y0 - 2,
        bounds.x1 + 70,
        bounds.y1 + 3,
    )

    page.draw_rect(
        rect,
        color=None,
        fill=(1, 1, 1),
        overlay=True,
    )

    # Create a visible false claim as a raster image.
    replacement = original.replace(
        "Manager, AIA",
        "Director, AIA",
        1,
    )

    scale = 4

    image = Image.new(
        "RGB",
        (
            round(rect.width * scale),
            round(rect.height * scale),
        ),
        "white",
    )

    draw = ImageDraw.Draw(image)
    font = get_font(round(span["size"] * scale))

    draw.text(
        (round(2 * scale), 0),
        replacement,
        font=font,
        fill="black",
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    page.insert_image(
        rect,
        stream=buffer.getvalue(),
        keep_proportion=False,
        overlay=True,
    )

    # Export.
    doc.save(
        str(OUTPUT),
        garbage=4,
        deflate=True,
    )
    doc.close()

    # Check the PDF text layer.
    check = fitz.open(OUTPUT)
    extracted = check[0].get_text()

    print(f"[CREATED] {OUTPUT}")
    print("[VISUAL]", replacement)
    print("[TEXT LAYER]", original)

    print(
        "[EXTRACTED] Manager:",
        "Manager, AIA" in extracted,
    )

    print(
        "[EXTRACTED] Director:",
        "Director, AIA" in extracted,
    )

    check.close()


if __name__ == "__main__":
    generate()
