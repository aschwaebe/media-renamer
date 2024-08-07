import os
from pathlib import Path

import streamlit as st
from utils import folder_picker, next_free_path


def unpack_files(folder_path: Path):
    progress_bar = st.progress(0)
    file_paths = list(folder_path.glob("**/*.*"))
    n_files = len(file_paths)
    st.info(f"found {n_files} files in subfolders.")
    for i, file_path in enumerate(file_paths, 1):
        progress_bar.progress(i / n_files)
        new_path = folder_path / file_path.name
        new_path = next_free_path(new_path)
        if new_path.name != file_path.name:
            st.info(
                f"filename: {file_path.name} already exists. renaming to {new_path.name}"
            )
        os.rename(file_path, new_path)


def unpacker():
    st.subheader("Unpacker")
    st.markdown(
        "- Moves all media files (images and photos) to parent folder.\n"
        "- On name conflicts Files will be renamed."
    )

    if "unpacker_folder_path" not in st.session_state:
        st.session_state.unpacker_folder_path = None
    if st.button("Select Folder", key="unpacker_folder_selector"):
        st.session_state.unpacker_folder_path = folder_picker()
    if st.session_state.unpacker_folder_path:
        st.text_input(
            "Selected folder:",
            st.session_state.unpacker_folder_path,
            key="selected_folder_unpacker",
        )
    if st.button("Unpack from subfolders!", key="unpacker_button"):
        folder_path = st.session_state.unpacker_folder_path
        if folder_path and os.path.isdir(folder_path):
            st.write(folder_path)
            unpack_files(Path(folder_path))
            st.success("All Files unpacked")
        else:
            st.error("The provided folder path is not valid.")
