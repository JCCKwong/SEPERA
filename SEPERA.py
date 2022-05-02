"""
Title: Development, multi-institutional validation, and algorithmic audit of SEPERA - An artificial intelligence-based
 Side-specific Extra-Prostatic Extension Risk Assessment tool for patients undergoing radical prostatectomy.
"""

# Import packages and libraries
import pandas as pd
import numpy as np
import PIL.Image
import streamlit as st
import joblib
from PIL import ImageFont, ImageDraw, ImageOps
from persist import persist, load_widget_state

def main():
    if "page" not in st.session_state:
        # Initialize session state.
        st.session_state.update({
            # Default page.
            "page": "home",

            # Radio, selectbox and multiselect options.
            "options": ["Hello", "Everyone", "Happy", "Streamlit-ing"],

            # Default widget values.
            "text": "",
            "slider": 0,
            "checkbox": False,
            "radio": "Hello",
            "selectbox": "Hello",
            "multiselect": ["Hello", "Everyone"],
        })

    page = st.sidebar.radio("Select your page", tuple(PAGES.keys()), format_func=str.capitalize)

    PAGES[page]()


def page_home():
    st.write(
        f"""
        Settings values
        ---------------
        - **Input**: {st.session_state.text}
        - **Slider**: `{st.session_state.slider}`
        - **Checkbox**: `{st.session_state.checkbox}`
        - **Radio**: {st.session_state.radio}
        - **Selectbox**: {st.session_state.selectbox}
        - **Multiselect**: {", ".join(st.session_state.multiselect)}
        """
    )


def page_settings():
    st.header("Change settings")

    st.text_input("Input", key=persist("text"))
    st.slider("Slider", 0, 10, key=persist("slider"))
    st.checkbox("Checkbox", key=persist("checkbox"))
    st.radio("Radio", st.session_state["options"], key=persist("radio"))
    st.selectbox("Selectbox", st.session_state["options"], key=persist("selectbox"))
    st.multiselect("Multiselect", st.session_state["options"], key=persist("multiselect"))


PAGES = {
    "home": page_home,
    "settings": page_settings,
}


if __name__ == "__main__":
    load_widget_state()
    main()
