# Renamer
- Simple tool to select a folder and rename photos and videos (.mp4 only) based on exif tags and video data.
- Media can optionally be organized in year/quarter subfolders.
- BeCareful since originals will not be backuped.
- Duplicates will be detected based on file hash and will be copied into duplicated folders.

# Unpacker
unpacks all media inside a subfolder in the chosen root folder.

# Inferrer
- infers events from a given folder by selecting subfolders name.
- event start and event end is infered by maximum and minum date inside the folders.

# Comparer
- detects duplicates in a chosen folder and subfolders based on hashvalues.

# Notes
- Do not use this tool on the original folder.
- Poetry must be installed.
- If you want to use it for .mp4 renaming ffmpeg must be installed.
    You can add ffmpeg (ffprobe.exe) to your PATH variable or place it in the same folder you run the script from.

# Getting Started
1. run poetry install
2. poetry shell
3. streamlit run app.py in app subfolder.