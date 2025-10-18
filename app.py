import streamlit as st
import os
import time
import glob
import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

# -------------------------------------------------
# Variables / estado inicial
# -------------------------------------------------
text = " "

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)

# limpiar archivos viejos (7 días por defecto)
remove_files(7)

# -------------------------------------------------
# Interfaz - narrativa y estilo ligero
# -------------------------------------------------
st.set_page_config(page_title="Lector de Textos → Voz", layout="centered")

st.title("Lector de Textos — Voz y Memoria")
st.subheader("Convierte una imagen en palabra hablada")

st.markdown(
    """
    > Imagina que tienes una nota antigua, un folio con instrucciones o una foto con texto: 
    > aquí la máquina lee por ti. Sube la imagen o toma una foto, deja que hagamos OCR, 
    > tradúcelo si lo deseas y genera un audio para escuchar o descargar.
    """
)

# opción de cámara (misma variable, texto personalizado)
cam_ = st.checkbox("Usar cámara 📷 (tomar foto en el momento)")

if cam_:
    img_file_buffer = st.camera_input("Apunta y captura")
else:
    img_file_buffer = None

# Sidebar con pasos e instrucciones
with st.sidebar:
    st.subheader("Guía rápida")
    st.write(
        "1. Elige si tomas una foto o subes una imagen.\n\n"
        "2. Si tomas foto, opcionalmente aplica un filtro para mejorar OCR.\n\n"
        "3. Elige idioma de entrada y salida, selecciona acento y presiona **Convertir a audio**."
    )
    st.markdown("---")
    st.subheader("Procesamiento para cámara")
    filtro = st.radio("Aplicar filtro de contraste para la foto", ("Con Filtro", "Sin Filtro"))

# Subida de imagen
bg_image = st.file_uploader("Arrastra o selecciona una imagen (png, jpg)", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada — previsualización abajo', use_container_width=True)

    # Guardar la imagen en el sistema de archivos (misma lógica)
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    st.success(f"Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.markdown("### Texto reconocido (OCR)")
    st.write(text)

# Si se usa cámara (buffer)
if img_file_buffer is not None:
    # Leer buffer como imagen OpenCV
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Aplicar filtro si el usuario lo pidió
    if filtro == 'Con Filtro':
        cv2_img = cv2.bitwise_not(cv2_img)
    else:
        cv2_img = cv2_img

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.markdown("### Texto reconocido (OCR) — captura de cámara")
    st.write(text)

# -------------------------------------------------
# Parámetros de traducción y salida (sidebar)
# -------------------------------------------------
with st.sidebar:
    st.subheader("Parámetros de traducción y voz")

    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()

    in_lang = st.selectbox(
        "Seleccione el idioma de entrada",
        ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"),
    )
    if in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Bengalí":
        input_language = "bn"
    elif in_lang == "Coreano":
        input_language = "ko"
    elif in_lang == "Mandarín":
        input_language = "zh-cn"
    elif in_lang == "Japonés":
        input_language = "ja"

    out_lang = st.selectbox(
        "Seleccione el idioma de salida",
        ("Inglés", "Español", "Bengalí", "Coreano", "Mandarín", "Japonés"),
    )
    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Bengalí":
        output_language = "bn"
    elif out_lang == "Coreano":
        output_language = "ko"
    elif out_lang == "Mandarín":
        output_language = "zh-cn"
    elif out_lang == "Japonés":
        output_language = "ja"

    english_accent = st.selectbox(
        "Seleccione el acento para la voz (gTTS)",
        (
            "Default",
            "India",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "Ireland",
            "South Africa",
        ),
    )

    if english_accent == "Default":
        tld = "com"
    elif english_accent == "India":
        tld = "co.in"
    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "United States":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Ireland":
        tld = "ie"
    elif english_accent == "South Africa":
        tld = "co.za"

    display_output_text = st.checkbox("Mostrar texto de salida (traducido)")

    # Botón de conversión (texto cambiado, misma funcionalidad)
    if st.button("Convertir a audio ▶️"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Reproducción")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("### Texto de salida (para tu referencia)")
            st.write(f"{output_text}")

st.markdown(
    """
    ---
    **Nota:** El reconocimiento OCR funciona mejor con imágenes nítidas y texto horizontal. 
    Si la imagen está borrosa o tiene sombras, intenta mejorar la iluminación o usar la opción de filtro.
    """
)





 
    
    
