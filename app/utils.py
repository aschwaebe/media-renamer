import hashlib
import tkinter as tk
from datetime import datetime
from pathlib import Path
from subprocess import check_output
from tkinter import filedialog

import ffmpeg
import streamlit as st
from PIL import Image

EXIF_TAGS = {
    "DateTime": 306,
    "DateTimeOriginal": 36867,
}

IMAGE_ENDINGS = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
VIDEO_ENDINGS = (".mp4",)
FILE_ENDINGS = IMAGE_ENDINGS + VIDEO_ENDINGS
N_HASH = 6


def remove_streamlit_head():
    st.markdown(
        """
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        section[data-testid="stSidebar"] div:first-child {
            top: 0;
            height: 100vh;
        }
        .block-container {
            margin-top:-100px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


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


def get_date(file_path) -> datetime:
    """
    Retrieves the date from the given file.

    Parameters:
        file_path (str): The path to the file from which to retrieve the EXIF tag.

    Returns:
        datetime.datetime or None: The datetime value of the EXIF tag if it exists,
        otherwise None. For videos ffmpeg is used.

    Raises:
        None

    Notes:
        - This function checks if the file path ends with the supported image or video
          file extensions.
        - If the file is an image, it opens the image using the PIL library and retrieves
          the EXIF data. It then extracts the date and time from the EXIF data and
          returns it as a datetime object.
        - If the file is a video, it uses the ffmpeg library to probe the video metadata.
          It iterates over the streams in the metadata and checks if the stream contains
          the "creation_time" tag. If it does, it retrieves the creation time and returns
          it as a datetime object.
        - If the file path does not end with a supported file extension or if the EXIF tag
          cannot be found, None is returned.
    """
    if str(file_path).lower().endswith(IMAGE_ENDINGS):
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            date_str = exif_data.get(EXIF_TAGS["DateTime"]) or exif_data.get(
                EXIF_TAGS["DateTimeOriginal"]
            )
            if date_str is not None:
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")

    if str(file_path).lower().endswith(VIDEO_ENDINGS):
        metadata = ffmpeg.probe(file_path)
        for stream in metadata.get("streams", []):
            if "tags" in stream and "creation_time" in stream["tags"]:
                creation_time = stream["tags"]["creation_time"]
                return datetime.strptime(creation_time, "%Y-%m-%dT%H:%M:%S.%fZ")

    return None


def get_date_components(date_obj):
    """
    Extracts the year, quarter, month, day, hour, minute, and second from the given date object.

    Parameters:
        date_obj (datetime.datetime): The date object from which to extract the date and time information.

    Returns:
        tuple: A tuple containing the year, quarter, month, day, hour, minute, and second.
    """
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
