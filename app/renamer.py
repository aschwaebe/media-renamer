import os
from pathlib import Path

import streamlit as st
from utils import (
    FILE_ENDINGS,
    IMAGE_ENDINGS,
    VIDEO_ENDINGS,
    add_hash,
    compute_file_hash,
    folder_picker,
    get_date,
    get_date_components,
    next_free_path,
)


def rename_and_move_media(folder_path: Path, move_files: str):
    progress_bar = st.progress(0)
    file_paths = [
        file
        for file in folder_path.glob("*.*")
        if file.suffix.lower().endswith(FILE_ENDINGS)
    ]
    n_files = len(file_paths)
    for i, file_path in enumerate(file_paths, 1):
        progress_bar.progress(i / n_files)

        try:
            exif_tag_value = get_date(file_path)
        except Exception as e:
            st.info(f"{e}: Could not read exif tag from {file_path}. Skipping File.")
            continue
        if not exif_tag_value:
            st.info(f"No exif data found for {file_path}. Skipping File.")
            continue

        try:
            year, quarter, month, day, hour, minute, second = get_date_components(
                exif_tag_value
            )
            file_base = f"{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}"
            file_extension = file_path.suffix.lower()
            new_filename = f"{file_base}{file_extension}"

            if move_files == "move to YYYY_Verschiedenes folder":
                target_folder_path = folder_path / f"{year}_Verschiedenes"
                os.makedirs(target_folder_path, exist_ok=True)
            elif move_files == "move to YYYY_QQ subolders":
                target_folder_path = folder_path / f"{year}_Q{quarter}"
                os.makedirs(target_folder_path, exist_ok=True)
            else:
                target_folder_path = folder_path

            duplicated_folder_path = folder_path / "duplicated"
            os.makedirs(duplicated_folder_path, exist_ok=True)
            new_file_path = target_folder_path / new_filename
            duplicated_file_path = duplicated_folder_path / new_filename

            if file_path == new_file_path:
                continue

            if new_file_path.exists():
                cur_file_hash = compute_file_hash(file_path)
                target_file_hash = compute_file_hash(new_file_path)

                if cur_file_hash == target_file_hash:
                    st.info(
                        f"duplicated files: {file_path} and {new_file_path} have the same hash: moving file to duplicated folder."
                    )
                    duplicated_file_path = next_free_path(duplicated_file_path)
                    os.rename(file_path, duplicated_file_path)
                    continue

                hash_new_file_path = add_hash(new_file_path, cur_file_hash)
                if not hash_new_file_path.exists():
                    os.rename(file_path, hash_new_file_path)
                    st.info(
                        f"File {new_file_path} already exists in the target folder (different hash value). Renaming new file to {hash_new_file_path}"
                    )
                    continue

                # its actually the hash of the target file name: %DATE_%TIME_%HASH.%EXT
                hash_new_file_path_hash = compute_file_hash(hash_new_file_path)
                if cur_file_hash == hash_new_file_path_hash:
                    st.info(
                        f"duplicated files: {file_path} and {hash_new_file_path}: have the same hash: movingfile  to duplicated folder."
                    )
                    duplicated_file_path = next_free_path(
                        add_hash(duplicated_file_path, hash_new_file_path_hash)
                    )
                    os.rename(file_path, duplicated_file_path)
                    continue

                # if hashes are not the same / should not happen
                st.warning(
                    f"short hashes are the same so renaming to next free file name. {hash_new_file_path}"
                )
                hash_new_file_path = next_free_path(hash_new_file_path)
                os.rename(file_path, hash_new_file_path)
            else:
                os.rename(file_path, new_file_path)
        except Exception as e:
            st.error(f"Error processing file {file_path}: ERROR: {e}")


# TODO RENAMING AND DUPLICATES DOES NOT WORK WITHOUT REORGANIZING!
# TODO BUGGEDm
def media_renamer():
    st.subheader("Media Renamer")
    st.markdown(
        "- Renames media files in a given folder"
        "based on exif or video date information.\n"
        "- Renamed files can be organized in date/quarter subfolders.\n"
        "- Duplicate files (based on hash) will be put in a duplicated folders.\n"
        "- files will be renamed on name conflict."
    )

    if "folder_path" not in st.session_state:
        st.session_state.folder_path = None
    if "move_files" not in st.session_state:
        st.session_state.move_files = False
    if st.button("Select Folder", "RenamerFolderSelector"):
        st.session_state.folder_path = folder_picker()
    if st.session_state.folder_path:
        st.text_input(
            "Selected folder:",
            st.session_state.folder_path,
            key="selected_folder_renamer",
        )
        n_images = len(
            [
                file
                for file in os.listdir(st.session_state.folder_path)
                if str(file).lower().endswith(IMAGE_ENDINGS)
            ]
        )
        n_videos = len(
            [
                file
                for file in os.listdir(st.session_state.folder_path)
                if str(file).lower().endswith(VIDEO_ENDINGS)
            ]
        )
        st.info(
            f"{n_images + n_videos} media files ({n_images} images and {n_videos} videos) found."
        )
    options = [
        "keep files in root folder",
        "move to YYYY_Verschiedenes folder",
        "move to YYYY_QQ subolders",
    ]
    move_files = st.radio("Do you want to move files?", options)

    st.session_state.move_files = move_files
    if st.button("Run Renamer!"):
        folder_path = st.session_state.folder_path
        if folder_path and os.path.isdir(folder_path):
            st.write(folder_path)
            rename_and_move_media(Path(folder_path), st.session_state.move_files)
            st.success(
                "Photos and Videos have been renamed and organized successfully!"
            )
        else:
            st.error("The provided folder path is not valid.")
