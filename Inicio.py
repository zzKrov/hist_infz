import os
import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# -----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Generador de Cuentos Infantiles // Krov Industries",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# LÍNEA BASE VISUAL: NOCHE ESTRELLADA CÓSMICA Y FLUIDOS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&family=Spectral:ital,wght@0,600;1,400&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #070714 !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }

/* 1. Malla continua de gradientes */
.stApp {
    background: linear-gradient(135deg, #070714 0%, #11142e 30%, #1e1132 60%, #060611 100%) !important;
    background-size: 300% 300% !important;
    animation: cosmicShift 18s ease infinite alternate !important;
}

@keyframes cosmicShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Fluidos orgánicos */
.fluid-star-1 {
    position: fixed;
    top: 15%;
    left: -120px;
    width: 520px;
    height: 520px;
    background: radial-gradient(circle, rgba(255, 209, 102, 0.12) 0%, rgba(6, 214, 160, 0.03) 55%, transparent 75%);
    border-radius: 40% 60% 70% 30% / 50% 60% 40% 50%;
    filter: blur(85px);
    animation: starDrift1 20s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

.fluid-star-2 {
    position: fixed;
    bottom: 5%;
    right: -100px;
    width: 560px;
    height: 560px;
    background: radial-gradient(circle, rgba(6, 214, 160, 0.12) 0%, rgba(255, 209, 102, 0.03) 55%, transparent 75%);
    border-radius: 60% 40% 50% 50% / 40% 50% 60% 50%;
    filter: blur(90px);
    animation: starDrift2 24s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

@keyframes starDrift1 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(110px, 60px) scale(1.15); }
    100% { transform: translate(30px, 130px) scale(0.95); }
}

@keyframes starDrift2 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-100px, -70px) scale(1.2); }
    100% { transform: translate(-20px, -110px) scale(0.9); }
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #ffd166;
    text-transform: uppercase;
    margin-bottom: 2px;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(255, 209, 102, 0.35);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.8rem;
}

div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 680px !important;
    height: 380px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(255, 209, 102, 0.4) !important;
    border-radius: 12px !important;
    box-shadow: 0 14px 45px rgba(0, 0, 0, 0.9), 0 0 25px rgba(255, 209, 102, 0.2) !important;
}

div.stButton > button {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #ffd166 0%, #06d6a0 100%) !important;
    color: #070714 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 25px rgba(255, 209, 102, 0.35) !important;
    transition: all 0.25s ease !important;
}
</style>

<div class="fluid-star-1"></div>
<div class="fluid-star-2"></div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Configuración")
    api_key_input = st.text_input("Clave de API de OpenAI", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
    stroke_width = st.slider("Grosor de línea", 1, 30, 5)

st.markdown('<div class="brand-signature">Krov Industries · Creatividad Lúdica</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Generador de Historias Infantiles</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja cualquier escena o personaje y la IA construirá un cuento mágico</div>', unsafe_allow_html=True)

_, col_c, _ = st.columns([1, 4.5, 1])

with col_c:
    canvas_result = st_canvas(
        fill_color="rgba(255, 209, 102, 0.2)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#ffffff",
        height=380,
        width=680,
        drawing_mode="freedraw",
        key="kids_story_canvas",
    )

    st.write("")
    analyze_btn = st.button("Describir boceto", use_container_width=True)

def encode_img_arr(arr):
    img = Image.fromarray(arr.astype('uint8')).convert('RGB')
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

if "sketch_desc" not in st.session_state:
    st.session_state.sketch_desc = ""

if analyze_btn:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        st.warning("Introduce tu API Key en la barra lateral.")
    elif canvas_result.image_data is None:
        st.warning("Dibuja una figura antes de solicitar la interpretación.")
    else:
        with col_c:
            with st.spinner("Analizando boceto..."):
                try:
                    b64 = encode_img_arr(np.array(canvas_result.image_data)[:, :, :3])
                    client = OpenAI(api_key=api_key)
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": [{"type": "text", "text": "Describe brevemente en español lo que se observa en este boceto."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                        max_tokens=250
                    )
                    st.session_state.sketch_desc = resp.choices[0].message.content
                    st.markdown(f"**Descripción del dibujo:** {st.session_state.sketch_desc}")
                except Exception as e:
                    st.error(f"Error: {e}")

if st.session_state.sketch_desc:
    with col_c:
        st.divider()
        st.markdown("### ¿Deseas inventar un cuento?")
        if st.button("Crear historia infantil", use_container_width=True):
            with st.spinner("Escribiendo el cuento..."):
                try:
                    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
                    story_prompt = f"Basándote en esta descripción: '{st.session_state.sketch_desc}', crea un cuento infantil breve, tierno y creativo."
                    story_resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": story_prompt}],
                        max_tokens=600
                    )
                    st.markdown("#### 📖 Tu Cuento:")
                    st.write(story_resp.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error al generar la historia: {e}")
