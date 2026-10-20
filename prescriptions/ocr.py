import io
import re

import pytesseract
from django.conf import settings
from PIL import Image

from medications.models import Medicine

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

FREQUENCY_PATTERN = re.compile(
    r"(\d\s*-\s*\d\s*-\s*\d|once daily|twice daily|thrice daily|\d+\s*times?\s*(?:a|per)\s*day|"
    r"every\s*\d+\s*hours?|OD|BD|TDS|QID)",
    re.IGNORECASE,
)
DOSAGE_PATTERN = re.compile(r"(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|iu))", re.IGNORECASE)
DURATION_PATTERN = re.compile(r"(\d+\s*(?:day|days|week|weeks|month|months))", re.IGNORECASE)


def extract_text(uploaded_file):
    """Run OCR on an uploaded image or PDF file object and return the raw extracted text."""
    name = uploaded_file.name.lower()
    uploaded_file.seek(0)
    data = uploaded_file.read()
    uploaded_file.seek(0)

    if name.endswith(".pdf"):
        from pdf2image import convert_from_bytes

        pages = convert_from_bytes(data)
        return "\n".join(pytesseract.image_to_string(page) for page in pages)

    image = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(image)


def parse_prescription_text(text):
    """Heuristically split OCR text into medicine line-items and try to match each
    against the MEDICINE reference table."""
    known_medicines = list(Medicine.objects.all())
    items = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or len(line) < 3:
            continue

        matched = None
        for medicine in known_medicines:
            if medicine.name.lower() in line.lower():
                matched = medicine
                break

        dosage_match = DOSAGE_PATTERN.search(line)
        frequency_match = FREQUENCY_PATTERN.search(line)
        duration_match = DURATION_PATTERN.search(line)

        if not matched and not dosage_match and not frequency_match and not duration_match:
            continue

        items.append(
            {
                "raw_text": line,
                "medicine_id": matched.pk if matched else None,
                "medicine_name_guess": matched.name if matched else "",
                "dosage": dosage_match.group(1) if dosage_match else "",
                "frequency": frequency_match.group(1) if frequency_match else "",
                "duration": duration_match.group(1) if duration_match else "",
            }
        )

    return items
