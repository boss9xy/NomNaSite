import os
import cv2
import shutil
import numpy as np
import pandas as pd
import streamlit as st
from urllib.request import urlretrieve
from utils import load_models, get_patch


@st.cache
def download_assets():
    if os.path.exists('assets.zip'): return
    urlretrieve('https://nomnaftp.000webhostapp.com/assets.zip', 'assets.zip')
    shutil.unpack_archive('assets.zip', 'assets')
    
    
st.set_page_config(page_title='NomNaOCR Demo', page_icon="🇻🇳", layout='wide')
uploaded_file = st.file_uploader("Choose a file")
url = st.text_input('Image Url:', 'http://www.nomfoundation.org/data/kieu/1866/page01a.jpg')

st.write('')
download_assets()    
det_model, reg_model = load_models()
col1, col2, col3 = st.columns(3)
    
with col1:
    st.header('Input Image:')
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        st.image(bytes_data)
        with open('test.jpg', 'wb') as f:
            f.write(bytes_data)
    elif url: 
        urlretrieve(url, 'test.jpg')
        st.image('test.jpg')

with col2:
    st.header('Text Detection:')
    with st.spinner('Detecting bounding boxes contain text...'):
        raw_image, boxes, scores = det_model.predict_one_page('test.jpg')
        boxes = sorted(boxes, key=lambda box: (box[:, 0].max(), box[:, 1].min()))
        image = raw_image.copy()

        for idx, box in enumerate(boxes):
            box = box.astype(np.int32)
            org = (box[3][0] + box[0][0])//2, (box[3][1] + box[0][1])//2
            
            cv2.polylines(image, [box], color=(255, 0, 0), thickness=1, isClosed=True)
            cv2.putText(
                image, str(idx), org, cv2.FONT_HERSHEY_SIMPLEX, 
                fontScale=0.8, color=(0, 0, 255), thickness=2
            )
        st.image(image)
    
with col3:
    st.header('Text Recognition:')
    texts = {'Box Score': [], 'Text': []}
    
    with st.spinner('Recognizing text in each predicted bounding box...'):
        for idx, box in enumerate(boxes):
            patch = get_patch(raw_image, box)
            texts['Box Score'].append(f'{scores[idx]:.4f}')
            texts['Text'].append(reg_model.predict_one_patch(patch))
        st.table(texts)