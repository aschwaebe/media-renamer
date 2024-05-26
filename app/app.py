from file_renamer import file_comparer
from utils import remove_streamlit_head
import streamlit as st
from media_renamer import media_renamer
from unpacker import unpacker



remove_streamlit_head()

tab1, tab2, tab3 = st.tabs(["Renamer", "Unpacker", "File Comparer"])
with tab1:
    media_renamer()
with tab2:
    unpacker()
with tab3:
    file_comparer()

# IDEA COMPARE PIXELS FOR IMAGES / IF EXIFDATA DIFFERS!
