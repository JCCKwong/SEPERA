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
from pathlib import Path
from PIL import ImageFont, ImageDraw, ImageOps
from google_drive_downloader import GoogleDriveDownloader as gdd
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

    page = st.sidebar.radio("", tuple(PAGES.keys()))

    PAGES[page]()


def page_sepera():
    st.sidebar.header("Instructions")
    st.sidebar.markdown(
        """
    1. Enter your information on the right
        * All fields are required
        * If there is missing information, please enter -1 or Unknown for the missing fields
    1. Press the SUBMIT button
    1. SEPERA will output the following:
        * Probability of side-specific extraprostatic extension (tumour extending beyond the prostatic capsule) for the left and right prostatic lobe
        * Annotated prostate map showing location and severity of disease
    """
    )

    # Specify font size for annotated prostate diagram
    font = ImageFont.truetype('Images/Font.ttf', 80)

    # Load saved items from Google Drive
    Model_location = st.secrets['SEPERA']
    Data_location = st.secrets['Data']

    @st.cache(allow_output_mutation=True)
    def load_items():
        save_dest = Path('model')
        save_dest.mkdir(exist_ok=True)
        model_checkpoint = Path('model/SEPERA.pkl')
        data_checkpoint = Path('model/data.pkl')

        # download from Google Drive if model or features are not present
        if not model_checkpoint.exists():
            with st.spinner("Downloading ... this may take awhile! \n Don't stop it!"):
                gdd.download_file_from_google_drive(Model_location, model_checkpoint)
        if not data_checkpoint.exists():
            with st.spinner("Downloading ... this may take awhile! \n Don't stop it!"):
                gdd.download_file_from_google_drive(Data_location, data_checkpoint)

        model = joblib.load(model_checkpoint)
        data = joblib.load(data_checkpoint)
        return model, data

    model, data = load_items()

    # Load blank prostate as image objects from GitHub repository
    def load_images():
        image = PIL.Image.open('Images/Prostate diagram.png')
        return image

    image = load_images()

    # Define choices and labels for feature inputs
    CHOICES = {0: 'No', 1: 'Yes', -1: 'Unknown'}

    def format_func_yn(option):
        return CHOICES[option]

    G_CHOICES = {0: 'Normal',
                 1: 'ISUP Grade 1',
                 2: 'ISUP Grade 2',
                 3: 'ISUP Grade 3',
                 4: 'ISUP Grade 4',
                 5: 'ISUP Grade 5',
                 -1: 'Unknown'}

    def format_func_gleason(option):
        return G_CHOICES[option]

    # Input individual values in sidebar
    st.header("Enter Your Information")
    if st.button('Click here if you have received hormone therapy or radiation therapy for prostate cancer before your '
                 'radical prostatectomy'):
        st.warning('The results of SEPERA will not be applicable for you since this tool was only trained on patients '
                   'who did not receive hormone or radiation therapy prior to their surgery.')
    col1, col2, col3 = st.columns([1, 1, 1])

    with st.form(key="my_form"):
        col1.subheader("General Information")
        age = col1.number_input("Age (years)", -1, 100, 72, key=1)
        psa = col1.number_input("PSA (ng/ml)", -1.00, 200.00, 11.00, key=2)
        vol = col1.number_input("Prostate volume (ml)", -1.0, 300.0, 40.0, key=3)
        p_high = col1.number_input("% Gleason pattern 4/5 disease (0 to 100)", -1.00, 100.00, 20.00, key=4)
        perineural_inv = col1.selectbox("Perineural invasion", options=list(CHOICES.keys()),
                                      format_func=format_func_yn, index=1)

        col2.subheader("Left Biopsy Information")
        base_findings = col2.selectbox('Left BASE findings', options=list(G_CHOICES.keys()),
                                     format_func=format_func_gleason, index=3)
        base_p_inv = col2.number_input('Left BASE % core involvement (0 to 100)', -1.0, 100.0, value=30.0, key=5)
        mid_findings = col2.selectbox('Left MID findings', options=list(G_CHOICES.keys()),
                                    format_func=format_func_gleason,
                                    index=3)
        mid_p_inv = col2.number_input('Left MID % core involvement (0 to 100)', -1.0, 100.0, value=5.0, key=6)
        apex_findings = col2.selectbox('Left APEX findings', options=list(G_CHOICES.keys()),
                                     format_func=format_func_gleason, index=2)
        apex_p_inv = col2.number_input('Left APEX % core involvement (0 to 100)', -1.0, 100.0, value=100.0, key=7)
        pos_core = col2.number_input('Left # of positive cores', -1, 30, 5, key=8)
        taken_core = col2.number_input('Left # of cores taken', -1, 30, 6, key=9)

        col3.subheader("Right Biopsy Information")
        base_findings_r = col3.selectbox('Right BASE findings', options=list(G_CHOICES.keys()),
                                       format_func=format_func_gleason, index=1)
        base_p_inv_r = col3.number_input('Right BASE % core involvement (0 to 100)', -1.0, 100.0, value=5.0, key=10)
        mid_findings_r = col3.selectbox('Right MID findings', options=list(G_CHOICES.keys()),
                                      format_func=format_func_gleason, index=1)
        mid_p_inv_r = col3.number_input('Right MID % core involvement (0 to 100)', -1.0, 100.0, value=10.0, key=11)
        apex_findings_r = col3.selectbox('Right APEX findings', options=list(G_CHOICES.keys()),
                                       format_func=format_func_gleason, index=0)
        apex_p_inv_r = col3.number_input('Right APEX % core involvement (0 to 100)', -1.0, 100.0, value=0.0, key=12)
        pos_core_r = col3.number_input('Left # of positive cores', -1, 30, 2, key=13)
        taken_core_r = col3.number_input('Left # of cores taken', -1, 30, 6, key=14)

        submitted = st.form_submit_button(label='SUBMIT')

        if submitted:
            ### CHECK FOR ERRORS ###
            if (base_findings == 0 and base_p_inv != 0) or (mid_findings == 0 and mid_p_inv != 0) or (apex_findings == 0 and apex_p_inv != 0) or (base_findings_r == 0 and base_p_inv_r != 0) or (mid_findings_r == 0 and mid_p_inv_r != 0) or (apex_findings_r == 0 and apex_p_inv_r != 0):
                st.warning("Error: Please ensure % core involvement is set to 0 if the biopsy cores at that site are "
                           "Normal.")

            elif (base_findings == -1 and base_p_inv != -1) or (mid_findings == -1 and mid_p_inv != -1) or (apex_findings == -1 and apex_p_inv != -1) or (base_findings_r == -1 and base_p_inv_r != -1) or (mid_findings_r == -1 and mid_p_inv_r != -1) or (apex_findings_r == -1 and apex_p_inv_r != -1):
                st.warning("Error: Please ensure % core involvement is set to -1 if the biopsy cores at that site are "
                           "Unknown.")

            elif (pos_core > taken_core) or (pos_core_r > taken_core_r):
                st.warning("Error: The number of positive cores should be equal or less than the number of cores taken."
                           "")

            else:
                ### LEFT DATA STORAGE ###
                # Group site findings into a list
                gleason_t = [base_findings, mid_findings, apex_findings]

                # Group % core involvements at each site into a list
                p_inv_t = [base_p_inv, mid_p_inv, apex_p_inv]

                # Combine site findings and % core involvements into a pandas DataFrame and sort by descending Gleason
                # then descending % core involvement
                g_p_inv = pd.DataFrame({'Gleason': gleason_t, '% core involvement': p_inv_t})
                sort_g_p_inv = g_p_inv.sort_values(by=['Gleason', '% core involvement'], ascending=False)

                # Store a dictionary into a variable
                pt_data = {'Age at Biopsy': age,
                           'Worst Gleason Grade Group': sort_g_p_inv['Gleason'].max(),
                           'PSA density': psa / vol,
                           'Perineural invasion': perineural_inv,
                           '% positive cores': (pos_core / taken_core) * 100,
                           '% Gleason pattern 4/5': p_high,
                           'Max % core involvement': sort_g_p_inv['% core involvement'].max(),
                           'Base finding': base_findings,
                           'Base % core involvement': base_p_inv,
                           'Mid % core involvement': mid_p_inv,
                           'Apex % core involvement': apex_p_inv
                           }

                pt_features = pd.DataFrame(pt_data, index=[0])

                ### RIGHT DATA STORAGE ###
                # Group site findings into a list
                gleason_t_r = [base_findings_r, mid_findings_r, apex_findings_r]

                # Group % core involvements at each site into a list
                p_inv_t_r = [base_p_inv_r, mid_p_inv_r, apex_p_inv_r]

                # Combine site findings and % core involvements into a pandas DataFrame and sort by descending Gleason
                # then descending % core involvement
                g_p_inv_r = pd.DataFrame({'Gleason': gleason_t_r, '% core involvement': p_inv_t_r})
                sort_g_p_inv_r = g_p_inv_r.sort_values(by=['Gleason', '% core involvement'], ascending=False)

                # Store a dictionary into a variable
                pt_data_r = {'Age at Biopsy': age,
                             'Worst Gleason Grade Group': sort_g_p_inv_r['Gleason'].max(),
                             'PSA density': psa / vol,
                             'Perineural invasion': perineural_inv,
                             '% positive cores': (pos_core_r / taken_core_r) * 100,
                             '% Gleason pattern 4/5': p_high,
                             'Max % core involvement': sort_g_p_inv_r['% core involvement'].max(),
                             'Base finding': base_findings_r,
                             'Base % core involvement': base_p_inv_r,
                             'Mid % core involvement': mid_p_inv_r,
                             'Apex % core involvement': apex_p_inv_r
                             }

                pt_features_r = pd.DataFrame(pt_data_r, index=[0])

                ### ANNOTATED PROSTATE DIAGRAM ###
                # Create text to overlay on annotated prostate diagram, auto-updates based on user inputted values
                if base_findings <= 0 or base_p_inv <= 0:
                    base_L = str(G_CHOICES[base_findings]) + '\n' \
                         + '% core involvement: n/a'
                else:
                    base_L = str(G_CHOICES[base_findings]) + '\n' \
                         + '% core involvement: ' + str(base_p_inv)
                if mid_findings <= 0 or mid_p_inv <= 0:
                    mid_L = str(G_CHOICES[mid_findings]) + '\n' \
                         + '% core involvement: n/a'
                else:
                    mid_L = str(G_CHOICES[mid_findings]) + '\n' \
                         + '% core involvement: ' + str(mid_p_inv)
                if apex_findings <= 0 or apex_p_inv <= 0:
                    apex_L = str(G_CHOICES[apex_findings]) + '\n' \
                         + '% core involvement: n/a'
                else:
                    apex_L = str(G_CHOICES[apex_findings]) + '\n' \
                         + '% core involvement: ' + str(apex_p_inv)

                if base_findings_r <= 0 or base_p_inv_r <= 0:
                    base_R = str(G_CHOICES[base_findings_r]) + '\n' \
                         + '% core involvement: n/a'
                else:
                    base_R = str(G_CHOICES[base_findings_r]) + '\n' \
                         + '% core involvement: ' + str(base_p_inv_r)
                if mid_findings_r <= 0 or mid_p_inv_r <= 0:
                    mid_R = str(G_CHOICES[mid_findings_r]) + '\n' \
                         + '% core involvement: n/a'
                else:
                    mid_R = str(G_CHOICES[mid_findings_r]) + '\n' \
                         + '% core involvement: ' + str(mid_p_inv_r)
                if apex_findings_r <= 0 or apex_p_inv_r <= 0:
                    apex_R = str(G_CHOICES[apex_findings_r]) + '\n' \
                         + '% core involvement: n/a'
                else:
                    apex_R = str(G_CHOICES[apex_findings_r]) + '\n' \
                         + '% core involvement: ' + str(apex_p_inv_r)

                # Set conditions to show colour coded site images based on Gleason Grade Group for each site
                draw = ImageDraw.Draw(image)
                if base_findings == 1:
                    image_bl_G1 = PIL.Image.open('Images/Base 1.png').convert('RGBA')
                    image.paste(image_bl_G1, (495, 1615), mask=image_bl_G1)
                if base_findings == 2:
                    image_bl_G2 = PIL.Image.open('Images/Base 2.png').convert('RGBA')
                    image.paste(image_bl_G2, (495, 1615), mask=image_bl_G2)
                if base_findings == 3:
                    image_bl_G3 = PIL.Image.open('Images/Base 3.png').convert('RGBA')
                    image.paste(image_bl_G3, (495, 1615), mask=image_bl_G3)
                if base_findings == 4:
                    image_bl_G4 = PIL.Image.open('Images/Base 4.png').convert('RGBA')
                    image.paste(image_bl_G4, (495, 1615), mask=image_bl_G4)
                if base_findings == 5:
                    image_bl_G5 = PIL.Image.open('Images/Base 5.png').convert('RGBA')
                    image.paste(image_bl_G5, (495, 1615), mask=image_bl_G5)

                if mid_findings == 1:
                    image_ml_G1 = PIL.Image.open('Images/Mid 1.png').convert('RGBA')
                    image.paste(image_ml_G1, (495, 965), mask=image_ml_G1)  # 606
                if mid_findings == 2:
                    image_ml_G2 = PIL.Image.open('Images/Mid 2.png').convert('RGBA')
                    image.paste(image_ml_G2, (495, 965), mask=image_ml_G2)
                if mid_findings == 3:
                    image_ml_G3 = PIL.Image.open('Images/Mid 3.png').convert('RGBA')
                    image.paste(image_ml_G3, (495, 965), mask=image_ml_G3)
                if mid_findings == 4:
                    image_ml_G4 = PIL.Image.open('Images/Mid 4.png').convert('RGBA')
                    image.paste(image_ml_G4, (495, 965), mask=image_ml_G4)
                if mid_findings == 5:
                    image_ml_G5 = PIL.Image.open('Images/Mid 5.png').convert('RGBA')
                    image.paste(image_ml_G5, (495, 965), mask=image_ml_G5)

                if apex_findings == 1:
                    image_al_G1 = PIL.Image.open('Images/Apex 1.png').convert('RGBA')
                    image.paste(image_al_G1, (495, 187), mask=image_al_G1)
                if apex_findings == 2:
                    image_al_G2 = PIL.Image.open('Images/Apex 2.png').convert('RGBA')
                    image.paste(image_al_G2, (495, 187), mask=image_al_G2)
                if apex_findings == 3:
                    image_al_G3 = PIL.Image.open('Images/Apex 3.png').convert('RGBA')
                    image.paste(image_al_G3, (495, 187), mask=image_al_G3)
                if apex_findings == 4:
                    image_al_G4 = PIL.Image.open('Images/Apex 4.png').convert('RGBA')
                    image.paste(image_al_G4, (495, 187), mask=image_al_G4)
                if apex_findings == 5:
                    image_al_G5 = PIL.Image.open('Images/Apex 5.png').convert('RGBA')
                    image.paste(image_al_G5, (495, 187), mask=image_al_G5)

                if base_findings_r == 1:
                    image_br_G1 = PIL.ImageOps.mirror(PIL.Image.open('Images/Base 1.png')).convert('RGBA')
                    image.paste(image_br_G1, (1665, 1615), mask=image_br_G1)
                if base_findings_r == 2:
                    image_br_G2 = PIL.ImageOps.mirror(PIL.Image.open('Images/Base 2.png')).convert('RGBA')
                    image.paste(image_br_G2, (1665, 1615), mask=image_br_G2)
                if base_findings_r == 3:
                    image_br_G3 = PIL.ImageOps.mirror(PIL.Image.open('Images/Base 3.png')).convert('RGBA')
                    image.paste(image_br_G3, (1665, 1615), mask=image_br_G3)
                if base_findings_r == 4:
                    image_br_G4 = PIL.ImageOps.mirror(PIL.Image.open('Images/Base 4.png')).convert('RGBA')
                    image.paste(image_br_G4, (1665, 1615), mask=image_br_G4)
                if base_findings_r == 5:
                    image_br_G5 = PIL.ImageOps.mirror(PIL.Image.open('Images/Base 5.png')).convert('RGBA')
                    image.paste(image_br_G5, (1665, 1615), mask=image_br_G5)

                if mid_findings_r == 1:
                    image_mr_G1 = PIL.Image.open('Images/Mid 1.png').convert('RGBA')
                    image.paste(image_mr_G1, (1665, 965), mask=image_mr_G1)
                if mid_findings_r == 2:
                    image_mr_G2 = PIL.Image.open('Images/Mid 2.png').convert('RGBA')
                    image.paste(image_mr_G2, (1665, 965), mask=image_mr_G2)
                if mid_findings_r == 3:
                    image_mr_G3 = PIL.Image.open('Images/Mid 3.png').convert('RGBA')
                    image.paste(image_mr_G3, (1665, 965), mask=image_mr_G3)
                if mid_findings_r == 4:
                    image_mr_G4 = PIL.Image.open('Images/Mid 4.png').convert('RGBA')
                    image.paste(image_mr_G4, (1665, 965), mask=image_mr_G4)
                if mid_findings_r == 5:
                    image_mr_G5 = PIL.Image.open('Images/Mid 5.png').convert('RGBA')
                    image.paste(image_mr_G5, (1665, 965), mask=image_mr_G5)

                if apex_findings_r == 1:
                    image_ar_G1 = PIL.ImageOps.mirror(PIL.Image.open('Images/Apex 1.png')).convert('RGBA')
                    image.paste(image_ar_G1, (1665, 187), mask=image_ar_G1)
                if apex_findings_r == 2:
                    image_ar_G2 = PIL.ImageOps.mirror(PIL.Image.open('Images/Apex 2.png')).convert('RGBA')
                    image.paste(image_ar_G2, (1665, 187), mask=image_ar_G2)
                if apex_findings_r == 3:
                    image_ar_G3 = PIL.ImageOps.mirror(PIL.Image.open('Images/Apex 3.png')).convert('RGBA')
                    image.paste(image_ar_G3, (1665, 187), mask=image_ar_G3)
                if apex_findings_r == 4:
                    image_ar_G4 = PIL.ImageOps.mirror(PIL.Image.open('Images/Apex 4.png')).convert('RGBA')
                    image.paste(image_ar_G4, (1665, 187), mask=image_ar_G4)
                if apex_findings_r == 5:
                    image_ar_G5 = PIL.ImageOps.mirror(PIL.Image.open('Images/Apex 5.png')).convert('RGBA')
                    image.paste(image_ar_G5, (1665, 187), mask=image_ar_G5)

                # Overlay text showing Gleason Grade Group, % positive cores, and % core involvement for each site
                draw.text((655, 1920), base_L, fill="black", font=font, align="center")
                draw.text((655, 1190), mid_L, fill="black", font=font, align="center")
                draw.text((735, 545), apex_L, fill="black", font=font, align="center")
                draw.text((1850, 1920), base_R, fill="black", font=font, align="center")
                draw.text((1850, 1190), mid_R, fill="black", font=font, align="center")
                draw.text((1770, 545), apex_R, fill="black", font=font, align="center")

                col4, col5 = st.columns([1, 2])
                left_prob = str((model.predict_proba(pt_features)[:, 1] * 100).round())[1:-2]
                right_prob = str((model.predict_proba(pt_features_r)[:, 1] * 100).round())[1:-2]

                ### SIMILAR CASE FINDER ###
                query = data[(data['Age at Biopsy'].between(pt_features['Age at Biopsy'][0] - 5,
                                                       pt_features['Age at Biopsy'][0] + 5)) &
                             (data['Worst Gleason Grade Group'] == pt_features['Worst Gleason Grade Group'][0]) &
                             (data['PSA density'].between(pt_features['PSA density'][0] * 0.7,
                                                        pt_features['PSA density'][0] * 1.3)) &
                             (data['Perineural invasion'] == pt_features['Perineural invasion'][0]) &
                             (data['% positive cores'].between(pt_features['% positive cores'][0] - 10,
                                                             pt_features['% positive cores'][0] + 10)) &
                             (data['% Gleason pattern 4/5'].between(pt_features['% Gleason pattern 4/5'][0] - 10,
                                                                  pt_features['% Gleason pattern 4/5'][0] + 10)) &
                             (data['Max % core involvement'].between(pt_features['Max % core involvement'][0] - 10,
                                                                   pt_features['Max % core involvement'][0] + 10))
                             ]
                pos_ssEPE = sum(query['ssEPE'])
                similar_cases = len(query['ssEPE'])

                query_r = data[(data['Age at Biopsy'].between(pt_features_r['Age at Biopsy'][0] - 5,
                                                            pt_features_r['Age at Biopsy'][0] + 5)) &
                             (data['Worst Gleason Grade Group'] == pt_features_r['Worst Gleason Grade Group'][0]) &
                             (data['PSA density'].between(pt_features_r['PSA density'][0] * 0.7,
                                                          pt_features_r['PSA density'][0] * 1.3)) &
                             (data['Perineural invasion'] == pt_features_r['Perineural invasion'][0]) &
                             (data['% positive cores'].between(pt_features_r['% positive cores'][0] - 10,
                                                               pt_features_r['% positive cores'][0] + 10)) &
                             (data['% Gleason pattern 4/5'].between(pt_features_r['% Gleason pattern 4/5'][0] - 10,
                                                                    pt_features_r['% Gleason pattern 4/5'][0] + 10)) &
                             (data['Max % core involvement'].between(pt_features_r['Max % core involvement'][0] - 10,
                                                                     pt_features_r['Max % core involvement'][0] + 10))
                             ]
                pos_ssEPE_r = sum(query_r['ssEPE'])
                similar_cases_r = len(query_r['ssEPE'])

                ### DISPLAY RESULTS ###
                col4.header('Your Results')
                col4.subheader('Probability of LEFT extraprostatic extension: {}%'.format(left_prob))
                col4.caption('For every 10 patients with your disease profile, about {} patients will have tumour that '
                             'has extended beyond the left side of the prostate.'
                             .format(str((model.predict_proba(pt_features)[:, 1] * 10).round())[1:-2]))
                if similar_cases == 0:
                    col4.caption('No patients with similar characteristics were found in our database.')
                else:
                    col4.caption("From our database, {:} out of {:} patients ({:}%) with similar characteristics "
                                 "on the left side had left extraprostatic extension."
                                 .format(pos_ssEPE, similar_cases, round((pos_ssEPE/similar_cases)*100)))
                col4.subheader('Probability of RIGHT extraprostatic extension: {}%'.format(right_prob))
                col4.caption('For every 10 patients with your disease profile, about {} patients will have tumour that '
                             'has extended beyond the right side of the prostate.'
                           .format(str((model.predict_proba(pt_features_r)[:, 1] * 10).round())[1:-2]))
                if similar_cases_r == 0:
                    col4.caption('No patients with similar characteristics were found in our database.')
                else:
                    col4.caption("From our database, {:} out of {:} patients ({:}%) with similar characteristics "
                                 "on the right side had right extraprostatic extension."
                                 .format(pos_ssEPE_r, similar_cases_r, round((pos_ssEPE_r/similar_cases_r)*100)))
                col5.header('Prostate Diagram')
                col5.image(image, use_column_width=True)







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

    For more information, the full manuscript is available [here](#).
    """
    )
    st.sidebar.header("Contributing Institutions")
    st.sidebar.write("""""")
    st.sidebar.image("Images/UHN.png", caption="University Health Network, Toronto, Canada")
    st.sidebar.write("""""")
    st.sidebar.image("Images/THP.png", caption="Trillium Health Partners, Mississauga, Canada")
    st.sidebar.write("""""")
    st.sidebar.image("Images/IMM.png", caption="L'Institut Mutualiste Montsouris, Paris, France")
    st.sidebar.write("""""")
    st.sidebar.image("Images/JB.png", caption="Jules Bordet Institute, Brussels, Belgium")


PAGES = {
    "SEPERA": page_sepera,
    "About": page_about,
}


if __name__ == "__main__":
    st.set_page_config(page_title="SEPERA - Side-Specific Extra-Prostatic Extension Risk Assessment",
                       page_icon="https://www.pikpng.com/pngl/b/174-1748384_prostate-cancer-ribbon-png-png-download-"
                                 "world-mental.png",
                       layout="wide",
                       initial_sidebar_state="auto"
                       )
    load_widget_state()
    main()
