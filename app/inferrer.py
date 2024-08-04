import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from utils import FILE_ENDINGS, folder_picker, get_date, next_free_path


def infer_events(folder_path: Path):
    """
    Infer events from media files in the given folder path.

    Args:
        folder_path (Path): The path to the folder containing media files.

    Returns:
        None
    """
    main_progress_bar = st.progress(0)
    sub_progress_bar = st.progress(0)
    file_paths = [
        file
        for file in list(folder_path.glob("**/*.*"))
        if str(file).lower().endswith(FILE_ENDINGS)
    ]
    n_files = len(file_paths)
    st.info(f"found {n_files} files in subfolders to analyze.")

    sub_folder_paths = [dir for dir in folder_path.glob("*") if dir.is_dir()]
    n_subfolders = len(sub_folder_paths)
    st.info(f"found {n_subfolders} subfolders in chosen folder: {folder_path}")

    # TODO SKIPPING Q1 folders as OPTION!
    events = list()
    for i_sf, sub_folder_path in enumerate(sub_folder_paths, 1):
        main_progress_bar.progress(i_sf / n_subfolders)
        media_files = [
            file
            for file in list(sub_folder_path.glob("**/*.*"))
            if str(file).lower().endswith(FILE_ENDINGS)
        ]
        n_media_files = len(media_files)
        dates: list[datetime] = []
        for i_fl, file_path in enumerate(media_files, 1):
            sub_progress_bar.progress(i_fl / n_media_files)
            try:
                file_date = get_date(file_path)
                if file_date:
                    dates.append(file_date)
            except Exception as e:
                st.error(f"Error processing file {file_path}: {e}")

        try:
            start = min(dates).strftime("%d.%m.%Y")
        except Exception as e:
            st.error(f"couldnt get minimum date for {sub_folder_path}: {e}")
            end = None

        try:
            end = max(dates).strftime("%d.%m.%Y")
        except Exception as e:
            st.error(f"couldnt get maximum date for {sub_folder_path}: {e}")
            end = None

        events.append(
            {
                "name": sub_folder_path.name,
                "start": start,
                "end": end,
            }
        )

    events_df = pd.DataFrame(events)
    st.dataframe(events_df)
    events_path = folder_path / "events.csv"
    events_path = next_free_path(events_path)
    events_df.to_csv(events_path, index=False)
    st.info(f"Infered {n_subfolders} Events. Saved events to {events_path}")


def events_inferer():
    st.subheader("Event Inferer")
    st.markdown(
        "- Takes a folder structure and will infer special events based on folder names\n"
        "- It will output a events.csv-file in the same folder with the following columns: event_name;start_date;end_date\n"
    )

    if "inferer_folder_path" not in st.session_state:
        st.session_state.inferer_folder_path = None
    if st.button("Select Folder", key="inferer_folder_selector"):
        st.session_state.inferer_folder_path = folder_picker()
    if st.session_state.inferer_folder_path:
        st.text_input("Selected folder:", st.session_state.inferer_folder_path)
    if st.button("Infer Events", key="inferer_button"):
        folder_path = st.session_state.inferer_folder_path
        if folder_path and os.path.isdir(folder_path):
            st.write(folder_path)
            infer_events(Path(folder_path))
        else:
            st.error("The provided folder path is not valid.")
