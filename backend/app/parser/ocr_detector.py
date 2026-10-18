import fitz  # PyMuPDF
from typing import Tuple


def detect_scanned_pdf(doc: fitz.Document, min_char_threshold: int = 80) -> Tuple[bool, bool, str]:
    """
    Evaluates whether a PyMuPDF Document is a scanned PDF (or image-only)
    with little or no extractable text.
    
    Returns:
        (is_scanned, ocr_recommended, explanation_message)
    """
    total_pages = len(doc)
    if total_pages == 0:
        return False, False, "Empty document with no pages."
    
    total_chars = 0
    has_images = False
    pages_with_little_text = 0
    
    for page in doc:
        text = page.get_text("text").strip()
        char_count = len(text)
        total_chars += char_count
        
        # Check if page has images
        images = page.get_images(full=True)
        if len(images) > 0:
            has_images = True
            
        if char_count < min_char_threshold:
            pages_with_little_text += 1

    avg_chars_per_page = total_chars / total_pages

    # Condition 1: Extremely low total characters (< 40 across document) but contains images
    if total_chars < 40 and has_images:
        return (
            True,
            True,
            "Scanned PDF detected: The document contains image layers with almost no extractable text. "
            "ATS software requires selectable digital text. OCR (Optical Character Recognition) is required "
            "to convert this into a searchable, machine-readable format."
        )

    # Condition 2: Majority of pages have fewer characters than threshold while images exist
    if pages_with_little_text == total_pages and avg_chars_per_page < min_char_threshold and has_images:
        return (
            True,
            True,
            f"Image-heavy document detected: Average extractable text is only {int(avg_chars_per_page)} characters per page. "
            "ATS parsers will likely fail to read your experience. Please provide a text-based PDF or DOCX."
        )

    # Condition 3: Completely zero characters extracted across all pages
    if total_chars == 0:
        return (
            True,
            True,
            "Zero text extracted: This document contains no machine-readable text. It is likely a scanned copy or photo. "
            "OCR processing is required to extract text."
        )

    return False, False, ""
