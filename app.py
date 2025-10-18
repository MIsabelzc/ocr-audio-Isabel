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

# ----------------------------
# CONFIG & STYLES (valores visuales)
# ----------------------------
st.set_page_config(page_title="BridgeSpeak — Tu puente de idiomas", layout="wide", initial_sidebar_state="expanded")

PRIMARY_BG = "linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%)"
CARD_BG = "rgba(255,255,255,0.04)"
TITLE_COLOR = "#ffffff"
TEXT_COLOR = "#e6eef6"
ACCENT = "#ffb86b"

st.markdown(
    f"""
    <style>
      /* Fondo general */
      [data-testid="stAppViewContainer"] > .main {{
        background: {PRIMARY_BG};
        background-attachment: fixed;
        color: {TEXT_COLOR};
      }}
      /* Tarjetas/boxes */
      .bridge-card {{
        background: {CARD_BG};
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.6);
        color: {TEXT_COLOR};
      }}
      h1, h2, h3 {{
        color: {TITLE_COLOR} !important;
      }}
      .small-muted {{
        color: rgba(255,255,255,0.7);
        font-size: 0.9em;
      }}
      .accent {{
        color: {ACCENT};
        font-weight: 700;
      }}
      /* Sidebar tweaks */
      [data-testid="stSidebar"] {{
        background: rgba(8,10,20,0.6);
        color: {TEXT_COLOR};
        padding: 18px;
        border-radius: 12px;
      }}
      /* Botones y audio */
      .stButton > button {{
        border-radius: 10px;
        padding: 8px 14px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# NARRATIVA / HEADER
# ----------------------------
st.title("BridgeSpeak — Tu puente de idiomas 🌍")
st.subheader("Transforma imágenes con texto en audio — entiende, practica y comparte")

st.markdown(
    """
    <div class="bridge-card">
    <strong>¿Para qué sirve BridgeSpeak?</strong>
    <p class="small-muted">
     BridgeSpeak te ayuda a <span class="accent">comprender textos en fotos</span>, practicarlos en voz alta y compartir el audio.
     Ideal para viajeros, estudiantes de idiomas o para comunicarte con extranjeros sin barreras.
    </p>
    <ul class="small-muted">
      <li>Captura texto desde una foto o sube una imagen.</li>
      <li>Aplica OCR para extraer las palabras.</li>
      <li>Traduce y genera audio con diferentes acentos.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# FUNCIONES (idénticas en lógica)
# ----------------------------
text = " "

def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    # guardar en carpeta temp
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

# limpieza automática (archivos de más de 7 días)
remove_files(7)

# ----------------------------
# LAYOUT PRINCIPAL: columnas
# ----------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown("### Captura / Subida")
    cam_ = st.checkbox("¿Quieres tomar una foto ahora? 📷")

    if cam_:
        img_file_buffer = st.camera_input("Apunta y captura — intenta enfocar el texto")
    else:
        img_file_buffer = None

    st.markdown("**O** sube una imagen con texto:")
    bg_image = st.file_uploader("", type=["png", "jpg", "jpeg"])

    # Mostrar la imagen y ejecutar OCR (misma lógica)
    if bg_image is not None:
        uploaded_file = bg_image
        st.image(uploaded_file, caption='Preview — imagen cargada', use_column_width=True)

        # Guardar la imagen (misma lógica)
        with open(uploaded_file.name, 'wb') as f:
            f.write(uploaded_file.read())

        st.success(f"Imagen guardada como {uploaded_file.name}")
        img_cv = cv2.imread(f'{uploaded_file.name}')
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)
        st.markdown("#### Texto detectado (OCR)")
        st.write(text)

    if img_file_buffer is not None:
        # To read image file buffer with OpenCV:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        # Filtro por defecto (se controla en sidebar)
        # (no se cambia la lógica, solo el texto o label)
        try:
            filtro_choice = filtro  # viene del sidebar
        except:
            filtro_choice = "Sin Filtro"

        if filtro_choice == 'Con Filtro':
            cv2_img = cv2.bitwise_not(cv2_img)
        else:
            cv2_img = cv2_img

        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)
        st.markdown("#### Texto detectado (Foto)")
        st.write(text)

    # Sugerencias para practicar (narrativa, no cambian lógica principal)
    st.markdown("---")
    st.markdown("### Practica con estas frases (ejemplo):")
    st.markdown(
        """
        - Hola, ¿puedes ayudarme con direcciones?
        - ¿Cuánto cuesta esto?
        - ¿Dónde está la estación de tren?
        - Estoy aprendiendo tu idioma, por favor corrígeme.
        """
    )

with right_col:
    # Panel lateral con instrucciones, filtro y parámetros (misma funcionalidad)
    st.markdown("## BridgeSpeak — Configuración 🔧")
    st.markdown("#### Ajustes para mejorar OCR")
    filtro = st.radio("Mejorar contraste / invertir colores (útil con texto oscuro/sobre fondo claro)", ('Sin Filtro', 'Con Filtro'))

    st.markdown("---")
    st.markdown("#### Idiomas y voz")

    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()

    # Mantenemos los selectboxes (texto y mapeo; ligeramente renombrados)
    in_lang = st.selectbox(
        "Idioma de origen (qué idioma contiene la imagen)",
        ("Detectar automáticamente", "Inglés", "Español", "Francés", "Alemán", "Italiano", "Portugués", "Ruso", "Árabe", "Hindi", "Chino (Mandarín)", "Japonés", "Coreano"),
    )
    if in_lang == "Detectar automáticamente":
        input_language = "auto"
    elif in_lang == "Inglés":
        input_language = "en"
    elif in_lang == "Español":
        input_language = "es"
    elif in_lang == "Francés":
        input_language = "fr"
    elif in_lang == "Alemán":
        input_language = "de"
    elif in_lang == "Italiano":
        input_language = "it"
    elif in_lang == "Portugués":
        input_language = "pt"
    elif in_lang == "Ruso":
        input_language = "ru"
    elif in_lang == "Árabe":
        input_language = "ar"
    elif in_lang == "Hindi":
        input_language = "hi"
    elif in_lang == "Chino (Mandarín)":
        input_language = "zh-cn"
    elif in_lang == "Japonés":
        input_language = "ja"
    elif in_lang == "Coreano":
        input_language = "ko"

    out_lang = st.selectbox(
        "Idioma de salida (voz)",
        ("Inglés", "Español", "Francés", "Alemán", "Italiano", "Portugués", "Ruso", "Árabe", "Hindi", "Chino (Mandarín)", "Japonés", "Coreano"),
    )
    if out_lang == "Inglés":
        output_language = "en"
    elif out_lang == "Español":
        output_language = "es"
    elif out_lang == "Francés":
        output_language = "fr"
    elif out_lang == "Alemán":
        output_language = "de"
    elif out_lang == "Italiano":
        output_language = "it"
    elif out_lang == "Portugués":
        output_language = "pt"
    elif out_lang == "Ruso":
        output_language = "ru"
    elif out_lang == "Árabe":
        output_language = "ar"
    elif out_lang == "Hindi":
        output_language = "hi"
    elif out_lang == "Chino (Mandarín)":
        output_language = "zh-cn"
    elif out_lang == "Japonés":
        output_language = "ja"
    elif out_lang == "Coreano":
        output_language = "ko"

    english_accent = st.selectbox(
        "Acento para la voz (solo para variantes inglesas)",
        (
            "Default",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "India",
            "Ireland",
            "South Africa",
        ),
    )

    if english_accent == "Default":
        tld = "com"
    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "United States":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "India":
        tld = "co.in"
    elif english_accent == "Ireland":
        tld = "ie"
    elif english_accent == "South Africa":
        tld = "co.za"

    display_output_text = st.checkbox("Mostrar texto traducido")

    st.markdown("---")
    st.markdown("### Acciones")
    # Al pulsar convertimos y mostramos progreso (UX visual, no cambia lógica)
    if st.button("Convertir a audio ▶️"):
        # Si el usuario eligió detección automática, intentamos detectar con googletrans
        if input_language == "auto" and text.strip():
            try:
                detected = translator.detect(text).lang
                input_language = detected
            except:
                input_language = "auto"

        # Barra de progreso para dar sensación de proceso (estético)
        progress = st.progress(0)
        for i in range(0, 101, 20):
            time.sleep(0.12)
            progress.progress(i)

        result, output_text = text_to_speech(input_language, output_language, text, tld)

        # Leer y reproducir audio (igual que antes), añadimos opción de descarga
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Reproducción — escucha tu texto")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Botón para descargar MP3
        st.download_button(
            label="Descargar audio (MP3)",
            data=audio_bytes,
            file_name=f"{result}.mp3",
            mime="audio/mpeg"
        )

        if display_output_text:
            st.markdown("### Texto de salida (traducido)")
            st.write(f"{output_text}")

# ----------------------------
# PIE / CONSEJOS
# ----------------------------
st.markdown("---")
st.markdown(
    """
    **Consejos de uso**  
    - Para mejores resultados: fotos en buena luz, texto horizontal y contraste alto.  
    - Usa el filtro si el texto está invertido o con fondo oscuro.  
    - Ideal para viajeros: captura carteles y escucha la pronunciación al instante.  
    """
)




 
    
    
