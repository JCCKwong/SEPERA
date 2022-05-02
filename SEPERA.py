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
            "page": "SEPERA"
        })
    st.title("SEPERA (Side-specific Extra-Prostatic Extension Risk Assessment)")
    st.sidebar.image("Images/Logo.png", use_column_width=True)
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Navigation", tuple(PAGES.keys()), format_func=str.capitalize)

    PAGES[page]()


def page_sepera():
    st.header("Instructions")
    st.markdown(
        """
    1. Enter patient values on the left
    1. Press submit button
    1. SEPERA will output the following:
        * Annotated prostate map showing location and severity of disease
        * Probability of side-specific extraprostatic extension (tumour extending beyond the prostatic capsule) 
        for the left and right prostatic lobe
    """
    )


def page_about():
    st.markdown(
        """
    Welcome to the Side-Specific Extra-Prostatic Extension Risk Assessment (SEPERA) tool. SEPERA provides several 
    outputs that may be beneficial for surgical planning and patient counselling for patients with localized prostate
    cancer:
    * Annotated prostate diagram showing location and severity of disease based on prostate biopsy
    * Probability of side-specific extraprostatic extension for the left and right prostatic lobe
    """
    )
    st.header("Reference")
    st.markdown(
        """
    **Development, multi-institutional validation, and algorithmic audit of SEPERA - An artificial intelligence-based 
    Side-specific Extra-Prostatic Extension Risk Assessment tool for patients undergoing radical prostatectomy.**\n

    *Jethro CC. Kwong$^{1,2}$, Adree Khondker$^{3}$, Eric Meng$^{4}$, Nicholas Taylor$^{3}$, Nathan Perlis$^{1}$, 
    Girish S. Kulkarni$^{1,2}$, Robert J. Hamilton$^{1}$, Neil E. Fleshner$^{1}$, Antonio Finelli$^{1}$, 
    Valentin Colinet$^{5}$, Alexandre Peltier$^{5}$, Romain Diamand$^{5}$, Yolene Lefebvre$^{5}$, 
    Qusay Mandoorah$^{6}$, Rafael Sanchez-Salas$^{6}$, Petr Macek$^{6}$, Xavier Cathelineau$^{6}$, 
    Martin Eklund$^{7}$, Alistair E.W. Johnson$^{2,8,9}$, Andrew H. Feifer$^{1}$, Alexandre R. Zlotta$^{1,10}$*\n

    1. Division of Urology, Department of Surgery, University of Toronto, Toronto, Ontario, Canada
    1. Temerty Centre for AI Research and Education in Medicine, University of Toronto, Toronto, Ontario, Canada
    1. Temerty Faculty of Medicine, University of Toronto, Toronto, Ontario, Canada
    1. Faculty of Medicine, Queen's University, Kingston, Ontario, Canada
    1. Jules Bordet Institute, Brussels, Belgium
    1. L'Institut Mutualiste Montsouris, Paris, France
    1. Department of Medical Epidemiology and Biostatistics, Karolinska Institutet, Stockholm, Sweden
    1. Division of Biostatistics, Dalla Lana School of Public Health, University of Toronto, Toronto, Ontario, Canada
    1. Vector Institute, Toronto, Ontario, Canada
    1. Division of Urology, Department of Surgery, Mount Sinai Hospital, University of Toronto, Toronto, Ontario, Canada

    For more information, the full manuscript is available [here] (#).
    """
    )
    st.header("Contributing Institutions")
    st.write("""""")
    st.image("Images/UHN.png", width=400, caption="University Health Network, Toronto, Ontario, Canada")
    st.write("""""")
    st.image("Images/THP.png", width=400, caption="Trillium Health Partners, Mississauga, Ontario, Canada")
    st.image("Images/IMM.png", width=400, caption="L'Institut Mutualiste Montsouris, Paris, France")
    st.image("Images/JB.png", width=400, caption="Jules Bordet Institute, Brussels, Belgium")


PAGES = {
    "SEPERA": page_sepera,
    "settings": page_about,
}


if __name__ == "__main__":
    st.set_page_config(page_title="SEPERA - Side-Specific Extra-Prostatic Extension Risk Assessment",
                       page_icon="📊",
                       layout="wide",
                       initial_sidebar_state="expanded"
                       )
    load_widget_state()
    main()
