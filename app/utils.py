import hashlib
import tkinter as tk
from datetime import datetime
from pathlib import Path
from subprocess import check_output
from tkinter import filedialog

import ffmpeg
from PIL import Image

EXIF_TAGS = {
    "DateTime": 306,
    "DateTimeOriginal": 36867,
}

IMAGE_ENDINGS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
VIDEO_ENDINGS = (".mp4",)
FILE_ENDINGS = IMAGE_ENDINGS + VIDEO_ENDINGS
N_HASH = 6


def folder_picker():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder:")
    root.destroy()
    return folder_path


def compute_file_hash(file_path, hash_algorithm="sha256"):
    hash_func = hashlib.new(hash_algorithm)
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def make_clickable(link):
    return f'<a href="{str(link).replace("///","//")}" target="_blank">{link}</a>'


def open_file(file_path):
    # Construct the shell command
    command = f"start {file_path}"
    # Run the shell command
    check_output(command, shell=True)


def get_exif_tag(file_path):
    if str(file_path).endswith(IMAGE_ENDINGS):
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            date_str = exif_data.get(EXIF_TAGS["DateTime"]) or exif_data.get(
                EXIF_TAGS["DateTimeOriginal"]
            )
            if date_str is not None:
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    if str(file_path).endswith(VIDEO_ENDINGS):
        metadata = ffmpeg.probe(file_path)
        for stream in metadata.get("streams", []):
            if "tags" in stream and "creation_time" in stream["tags"]:
                creation_time = stream["tags"]["creation_time"]
                return datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    return None


def extract_date_time(date_obj):
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    hour = date_obj.hour
    minute = date_obj.minute
    second = date_obj.second
    quarter = (month - 1) // 3 + 1
    return year, quarter, month, day, hour, minute, second


def next_free_path(path_: Path) -> Path:
    i = 1
    p = path_
    while path_.exists():
        path_ = p.parent / f"{p.stem}_{i}{p.suffix}"
        i += 1
    return path_


def add_hash(path_: Path, hash_: str) -> Path:
    """Adds hash / or other string to end of filename."""
    return path_.parent / f"{path_.stem}_{hash_[:N_HASH]}{path_.suffix}"
