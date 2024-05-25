import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st
from utils import FILE_ENDINGS, IMAGE_ENDINGS, VIDEO_ENDINGS, folder_picker, open_file


def compare_hashes(folder_path, hash_algorithm="sha256"):
    progress_bar = st.progress(0)
    file_paths = [
        file
        for file in Path(st.session_state.hash_folder_path).glob("**/*")
        if str(file).endswith(FILE_ENDINGS)
    ]
    n_files = len(file_paths)
    st.info(f"found {n_files} files.")
    file_hashes = []
    for i, file_path in enumerate(file_paths, 1):
        progress_bar.progress(i / n_files)
        if str(file_path).lower().endswith(FILE_ENDINGS):
            try:
                with open(file_path, "rb") as file:
                    file_hash = hashlib.file_digest(file, hash_algorithm).hexdigest()
                file_hashes.append(
                    {"file_path": str(file_path), "file_hash": file_hash}
                )

            except Exception as e:
                st.error(f"Error processing file {file_path}: {e}")

    data = pd.DataFrame(file_hashes)
    if len(data) > 0:
        data = data[data.duplicated("file_hash", keep=False)]
        data = data.sort_values(by="file_hash")
        data["file_hash"] = data["file_hash"].str.slice(stop=8)
    return data


def hash_analyzer():
    st.title("Hash Analyzer")
    if "hash_folder_path" not in st.session_state:
        st.session_state.hash_folder_path = None
    if st.button("Select Folder", "HashFolderSelector"):
        st.session_state.hash_folder_path = Path(folder_picker())
    if st.session_state.hash_folder_path:
        st.text_input("Selected folder:", st.session_state.hash_folder_path)
        n_images = len(
            [
                file
                for file in Path(st.session_state.hash_folder_path).glob("**/*")
                if str(file).endswith(IMAGE_ENDINGS)
            ]
        )
        n_videos = len(
            [
                file
                for file in Path(st.session_state.hash_folder_path).glob("**/*")
                if str(file).endswith(VIDEO_ENDINGS)
            ]
        )
        st.info(
            f"{n_images + n_videos} media files ({n_images} images and {n_videos} videos) found in folder and subfolders."
        )

    if st.button("Run Hash Analyzer!", "HashAnalyzerButton"):
        folder_path = st.session_state.hash_folder_path
        df = compare_hashes(folder_path)
        st.success("Photos and Videos have been analyzed succesfully.")
        # Display DataFrame with buttons
        st.write("## Files with Open Buttons")
        for index, row in df.iterrows():
            col1, col2 = st.columns([2, 1])
            col1.write(row["file_path"])
            # col2.write(row['file_hash'])
            if col2.button("Show Html file", key=row["file_path"]):
                open_file(row["file_path"])
