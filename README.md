# photo renamer
Simple tool to select a folder and rename photos and videos (.mp4 only) based on exif tags and video data.
Photos will be put into subfolder based on year and quarter and moved into it.
BeCareful since originals will not be backuped.

# Notes
Do not use this tool on the original folder.
Poetry must be installed.
If you want to use it for .mp4 renaming ffmpeg must be installed.
You can add ffmpeg (ffprobe.exe) add to you PATH variable or place it in the same folder you run the script from.

# Getting Started
1. run poetry install
2. poetry shell
3. streamlit run app.py in app subfolder.