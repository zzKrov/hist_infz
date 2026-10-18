import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# ============================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR)
# ============================================================
st.set_page_config(
    page_title="Generador de Cuentos // Krov Industries",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# ESTADO DEL LIENZO PARA LIMPIEZA EFECTIVA
# ------------------------------------------------------------
if "story_canvas_ver" not in st.session_state:
    st.session_state.story_canvas_ver = 0
if "story_desc" not in st.session_state:
    st.session_state.story_desc = ""

# ============================================================
# ESTILOS VISUALES: NOCHE CÓSMICA LÍQUIDA Y CENTRADO EXACTO
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&family=Spectral:ital,wght@0,600;1,400&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #060611 !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

/* Fondo líquido cósmico acelerado por GPU */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(255, 209, 102, 0.16) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(6, 214, 160, 0.14) 0%, transparent 45%),
        linear-gradient(135deg, #060611 0%, #10122b 50%, #060611 100%) !important;
    background-size: 200% 200% !important;
    animation: cosmicLava 15s ease infinite alternate !important;
}

@keyframes cosmicLava {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0% 100%; }
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
    margin-bottom: 1.4rem;
}

.block-container {
    max-width: 760px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}

/* Centrado del lienzo */
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
    border: 2px solid rgba(255, 209, 102, 0.35) !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 209, 102, 0.15) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}

iframe[title*="canvas"]:hover {
    border-color: #ffd166 !important;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.9), 0 0 30px rgba(255, 209, 102, 0.35) !important;
}

div.stButton > button[kind="primary"] {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #ffd166 0%, #06d6a0 100%) !important;
    color: #070714 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.75rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(255, 209, 102, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 35px rgba(255, 209, 102, 0.65) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(18, 20, 35, 0.85) !important;
    color: #e4e4e7 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 6px !important;
    padding: 0.75rem 1.6rem !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

.story-box {
    background: rgba(14, 18, 36, 0.88);
    border-left: 4px solid #ffd166;
    padding: 22px;
    border-radius: 8px;
    margin-top: 18px;
    line-height: 1.7;
    font-size: 1.05rem;
    font-family: 'Spectral', Georgia, serif;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CABECERA Y CONTROLES PRINCIPALES
# ============================================================
st.markdown('<div class="brand-signature">Krov Industries · Creatividad</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Generador de Cuentos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja una escena o personaje y la IA creará un relato adaptado</div>', unsafe_allow_html=True)

with st.container(border=True):
    c_key, c_stroke = st.columns([1.8, 1])
    with c_key:
        api_key = st.text_input("Clave de API de OpenAI:", type="password", value=os.environ.get("OPENAI_API_KEY", ""), placeholder="sk-...")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
    with c_stroke:
        stroke_w = st.slider("Grosor de lápiz:", 2, 25, 6)

# Lienzo centrado con clave dinámica para limpieza total
canvas_res = st_canvas(
    fill_color="rgba(255, 209, 102, 0.2)",
    stroke_width=stroke_w,
    stroke_color="#000000",
    background_color="#ffffff",
    height=380,
    width=680,
    drawing_mode="freedraw",
    key=f"cuento_canvas_v{st.session_state.story_canvas_ver}",
)

st.write("")
btn_col1, btn_col2 = st.columns([3, 1])
with btn_col1:
    btn_crear = st.button("Crear cuento a partir del dibujo", type="primary", use_container_width=True)
with btn_col2:
    btn_limpiar = st.button("Limpiar lienzo", type="secondary", use_container_width=True)

if btn_limpiar:
    st.session_state.story_canvas_ver += 1
    st.session_state.story_desc = ""
    st.rerun()

def codificar_imagen(arr):
    img = Image.fromarray(arr.astype('uint8')).convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# ============================================================
# INFERENCIA Y GENERACIÓN DEL CUENTO
# ============================================================
if btn_crear:
    key_val = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key_val:
        st.warning("Introduce una clave de API de OpenAI válida arriba.")
    elif canvas_res.image_data is None or not np.any(canvas_res.image_data[:, :, :3] < 250):
        st.warning("Dibuja una figura antes de solicitar el cuento.")
    else:
        with st.spinner("Interpretando el dibujo y redactando el cuento..."):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key_val)
                b64 = codificar_imagen(np.array(canvas_res.image_data)[:, :, :3])

                prompt = (
                    "Observa atentamente este dibujo. Identifica con exactitud los elementos o personajes trazados "
                    "y redacta un cuento infantil breve, original y emotivo en español donde esos elementos sean los protagonistas. "
                    "Incluye un título destacado al inicio."
                )
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                    max_tokens=650
                )
                st.session_state.story_desc = resp.choices[0].message.content
            except Exception as e:
                st.error(f"Error al generar el cuento: {e}")

if st.session_state.story_desc:
    st.markdown(f'<div class="story-box">{st.session_state.story_desc}</div>', unsafe_allow_html=True)
