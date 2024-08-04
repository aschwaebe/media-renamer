import streamlit as st
from comparer import file_comparer
from inferrer import events_inferer
from renamer import media_renamer
from unpacker import unpacker
from utils import remove_streamlit_head

remove_streamlit_head()

tab1, tab2, tab3, tab4 = st.tabs(
    ["Renamer", "Unpacker", "Event Inferer", "File Comparer"]
)
with tab1:
    media_renamer()
with tab2:
    unpacker()
with tab3:
    events_inferer()
with tab4:
    file_comparer()

# IDEA COMPARE PIXELS FOR IMAGES / IF EXIFDATA DIFFERS!
