import streamlit as st
from media_renamer import media_renamer
from unpacker import unpacker

# Function to run shell command to open the file

st.markdown(
    """
<style>
    #MainMenu, header, footer {visibility: hidden;}
    /* This code gets the first element on the sidebar,
    and overrides its default styling */
    section[data-testid="stSidebar"] div:first-child {
        top: 0;
        height: 100vh;
    }
</style>
""",
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Renamer", "Unpacker"])
with tab1:
    media_renamer()
with tab2:
    unpacker()
# with tab2:
#     hash_analyzer()

# TODO MOVE ALL TO TOP LEVEL FILES!
# TODO COMPARE PIXELS FOR IMAGES / IF EXIFDATA DIFFERS!
