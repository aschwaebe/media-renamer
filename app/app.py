import streamlit as st
import os
from PIL import Image
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import ffmpeg

st.markdown("""
<style>
    #MainMenu, header, footer {visibility: hidden;}

    /* This code gets the first element on the sidebar,
    and overrides its default styling */
    section[data-testid="stSidebar"] div:first-child {
        top: 0;
        height: 100vh;
    }
</style>
""", unsafe_allow_html=True)

EXIF_TAGS = {
    'DateTime': 306,
    'DateTimeOriginal': 36867,
}

IMAGE_ENDINGS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
VIDEO_ENDINGS = (".mp4",)
FILE_ENDINGS = IMAGE_ENDINGS + VIDEO_ENDINGS

def get_exif_tag(file_path):
    if str(file_path).endswith(IMAGE_ENDINGS):
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            date_str = exif_data.get(EXIF_TAGS['DateTime']) or exif_data.get(EXIF_TAGS['DateTimeOriginal'])
            if date_str is not None:
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    if str(file_path).endswith(VIDEO_ENDINGS):
        metadata = ffmpeg.probe(file_path)
        for stream in metadata.get('streams', []):
            if 'tags' in stream and 'creation_time' in stream['tags']:
                creation_time = stream['tags']['creation_time']
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

def rename_and_move_media(folder_path, move_files):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(FILE_ENDINGS):
            file_path = os.path.join(folder_path, filename)
            exif_tag_value = get_exif_tag(file_path)
            if exif_tag_value:
                try:
                    year, quarter, month, day, hour, minute, second = extract_date_time(exif_tag_value)
                    file_base = f"{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}"
                    file_extension = f"{os.path.splitext(filename)[1]}"
                    new_filename = f"{file_base}{file_extension}"
                    
                    if move_files:
                        target_folder_path = os.path.join(folder_path, f"{year}_Q{quarter}")
                        os.makedirs(target_folder_path, exist_ok=True)
                    else:
                        target_folder_path = folder_path

                    new_file_path = os.path.join(target_folder_path, new_filename)
                    if file_path == new_file_path:
                        st.info(f"File {file_path} is already named correctly.")
                    elif os.path.exists(new_file_path):
                        i=1
                        original_new_path = new_file_path
                        while os.path.exists(new_file_path):
                            new_file_path = os.path.join(target_folder_path, f"{file_base}_{i}{file_extension}")
                            i+=1
                        st.info(f"File {original_new_path} already exists in the target folder. Renaming file to {new_file_path}")
                        os.rename(file_path, new_file_path)
                    else:
                        os.rename(file_path, new_file_path)      

                except Exception as e:
                    st.error(f"Error processing file {filename}: {e}")

def folder_picker():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder:")
    root.destroy()
    return folder_path

st.title("Media Renamer")
if 'folder_path' not in st.session_state:
    st.session_state.folder_path = None
if 'move_files' not in st.session_state:
    st.session_state.move_files = False

if st.button('Select Folder'):
    st.session_state.folder_path = folder_picker()

if st.session_state.folder_path:
    st.text_input('Selected folder:', st.session_state.folder_path)
    n_images = len([file for file in os.listdir(st.session_state.folder_path) if str(file).endswith(IMAGE_ENDINGS)])
    n_videos = len([file for file in os.listdir(st.session_state.folder_path) if str(file).endswith(VIDEO_ENDINGS)])
    st.info(f"{n_images} images found.")
    st.info(f"{n_videos} videos found.")

# Add a checkbox for moving files
move_files = st.checkbox("Organize media in year/quarter YYYY_QQ subolders?", value=st.session_state.move_files)
st.session_state.move_files = move_files

if st.button("Run Renamer!"):
    folder_path = st.session_state.folder_path
    if folder_path and os.path.isdir(folder_path):
        st.write(folder_path)
        rename_and_move_media(folder_path, st.session_state.move_files)
        st.success("Photos and Videos have been renamed and organized successfully!")
    else:
        st.error("The provided folder path is not valid.")
