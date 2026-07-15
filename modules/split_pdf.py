import os
import re
from pypdf import PdfWriter, PdfReader


def get_page_count(pdf_path: str) -> int:
    """Return the total number of pages in a PDF."""
    reader = PdfReader(pdf_path)
    return len(reader.pages)


def parse_range_string(range_str: str) -> list:
    """
    Parse a range string like '1-3, 5, 7-10' into a list of (start, end) tuples.
    Single pages like '5' become (5, 5).
    """
    ranges = []
    for part in re.split(r"[,\s]+", range_str.strip()):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)-(\d+)", part)
        if m:
            ranges.append((int(m.group(1)), int(m.group(2))))
        elif re.fullmatch(r"\d+", part):
            n = int(part)
            ranges.append((n, n))
    return ranges


def split_by_ranges(pdf_path: str, ranges: list, output_dir: str) -> list:
    """
    Split PDF by list of (start, end) tuples (1-indexed, inclusive).
    Returns list of output file paths.
    """
    reader = PdfReader(pdf_path)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    output_files = []
    for idx, (start, end) in enumerate(ranges, start=1):
        writer = PdfWriter()
        for page_num in range(start - 1, end):  # convert to 0-indexed
            writer.add_page(reader.pages[page_num])
        out_name = f"{base}_part{idx}_p{start}-p{end}.pdf"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append(out_path)
    return output_files


def split_all_pages(pdf_path: str, output_dir: str) -> list:
    """
    Split every page of the PDF into its own file.
    Returns list of output file paths.
    """
    reader = PdfReader(pdf_path)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    output_files = []
    for idx, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_name = f"{base}_page{idx}.pdf"
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append(out_path)
    return output_files
