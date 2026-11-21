
import re
import zipfile
import xml.etree.ElementTree as ET
import zlib

from pathlib import Path
from datetime import date


# ---------------- READ WORD DOCUMENT ----------------

def read_word_document(path):

    text_parts = []

    with zipfile.ZipFile(path, "r") as docx:

        xml_data = docx.read("word/document.xml")

        root = ET.fromstring(xml_data)

        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

        for paragraph in root.findall(".//w:p", namespace):

            words = []

            for element in paragraph.findall(".//w:t", namespace):
                if element.text:
                    words.append(element.text)

            text_parts.append("".join(words))

    return "\n".join(text_parts)


# ---------------- READ PDF DOCUMENT ----------------

def read_pdf_document(path):

    text_parts = []

    with open(path, "rb") as file:
        pdf_data = file.read()

    # Find PDF streams
    streams = re.findall(
        rb"stream\r?\n(.*?)\r?\nendstream",
        pdf_data,
        re.DOTALL
    )

    for stream in streams:

        content = stream

        # Try decompressing Flate streams
        try:
            content = zlib.decompress(stream)
        except zlib.error:
            pass

        # Extract text inside PDF text operators
        for match in re.findall(
            rb"\((.*?)\)\s*Tj",
            content,
            re.DOTALL
        ):

            try:
                text_parts.append(
                    match.decode("utf-8", errors="ignore")
                )
            except Exception:
                continue

        # Extract text from hexadecimal strings
        for match in re.findall(
            rb"<([0-9A-Fa-f]+)>\s*Tj",
            content
        ):

            try:
                raw = bytes.fromhex(match.decode())

                if len(raw) >= 2 and raw.startswith(b"\xfe\xff"):
                    text_parts.append(raw.decode("utf-16-be", errors="ignore"))
                else:
                    text_parts.append(raw.decode("latin-1", errors="ignore"))

            except Exception:
                continue

    return "\n".join(text_parts)


# ---------------- READ DOCUMENT ----------------

def read_document(file_path):

    path = Path(file_path)

    extension = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError("The selected document does not exist.")

    if extension == ".docx":
        text = read_word_document(str(path))

    elif extension == ".pdf":
        text = read_pdf_document(str(path))

    else:
        raise ValueError(
            "Only PDF and DOCX documents are supported."
        )

    if not text.strip():
        raise ValueError(
            "No readable text was found. "
            "This PDF may use an unsupported text format "
            "or the document may contain only scanned images."
        )

    return text


# ---------------- IDENTIFY EXPENSE CATEGORY ----------------

def get_category(description):

    text = description.lower()

    categories = {
        "Food": ["food", "restaurant", "grocery"],
        "Transportation": ["travel", "taxi", "bus", "fuel"],
        "Shopping": ["shopping", "clothes"],
        "Education": ["education", "book", "course"],
        "Healthcare": ["medical", "medicine", "hospital"],
        "Bills": ["electricity", "bill", "recharge", "rent"],
        "Entertainment": ["movie", "game", "entertainment"]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return "Other"


# ---------------- EXTRACT EXPENSES ----------------

def extract_expenses(text):

    expenses = []

    amount_pattern = re.compile(
        r"(?:₹|Rs\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)",
        re.IGNORECASE
    )

    skip_words = [
        "grand total",
        "subtotal",
        "total",
        "amount due",
        "balance",
        "discount"
    ]

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if any(word in line.lower() for word in skip_words):
            continue

        matches = list(amount_pattern.finditer(line))

        if not matches:
            continue

        match = matches[-1]

        amount = float(
            match.group(1).replace(",", "")
        )

        if amount <= 0:
            continue

        description = (
            line[:match.start()] +
            line[match.end():]
        ).strip(" :-|")

        if not description:
            description = "Imported Expense"

        category = get_category(description)

        expenses.append({
            "title": description,
            "amount": amount,
            "category": category,
            "expense_date": date.today().isoformat(),
            "payment_method": "",
            "description": "Imported from document"
        })

    return expenses
