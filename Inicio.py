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
    page_title="Taller de Cuentos // Krov Industries",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "story_ver" not in st.session_state:
    st.session_state.story_ver = 0

# ============================================================
# ESTILOS: TALLER DE FANTASÍA Y NOCHE ESTRELLADA LÍQUIDA
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&family=Spectral:ital,wght@0,500;0,700;1,400&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #070714 0%, #15102d 40%, #20112c 70%, #060611 100%) !important;
    background-size: 300% 300% !important;
    animation: storyLava 16s ease infinite alternate !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

@keyframes storyLava {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #ffd166;
    text-transform: uppercase;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(255, 209, 102, 0.4);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.4rem;
}

.block-container {
    max-width: 820px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    margin: 0 auto !important;
}

/* Barra de herramientas infantiles */
.story-tools {
    background: rgba(18, 14, 34, 0.9);
    border: 1px solid rgba(255, 209, 102, 0.35);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 12px;
}

div[data-testid="stCustomComponentV1"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}

iframe[title*="canvas"] {
    width: 720px !important;
    height: 380px !important;
    margin: 0 auto !important;
    display: block !important;
    border: 2px solid rgba(255, 209, 102, 0.4) !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(255, 209, 102, 0.2) !important;
}

div.stButton > button[kind="primary"] {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #ffd166 0%, #06d6a0 100%) !important;
    color: #070714 !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.8rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(255, 209, 102, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 0 35px rgba(255, 209, 102, 0.7) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(18, 20, 35, 0.85) !important;
    color: #e4e4e7 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 6px !important;
    padding: 0.8rem 1.6rem !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="secondary"]:hover {
    transform: translateY(-2px) !important;
    border-color: #ffffff !important;
    color: #ffffff !important;
}

.storybook-card {
    background: rgba(18, 14, 36, 0.9);
    border-left: 4px solid #ffd166;
    padding: 24px;
    border-radius: 8px;
    margin-top: 18px;
    line-height: 1.7;
    font-size: 1.05rem;
    font-family: 'Spectral', Georgia, serif;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-signature">Krov Industries · Creatividad Lúdica</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Taller de Cuentos Ilustrados</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja una escena o personaje infantil y la IA redactará una historia original</div>', unsafe_allow_html=True)

# BARRA DE HERRAMIENTAS INFANTILES
st.markdown('<div class="story-tools">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([1.5, 0.9, 0.8, 1.1])
with c1:
    trazo = st.selectbox("Pincel:", ["🖍️ Pincel Mágico", "📏 Trazo Recto", "⏹️ Recuadro", "⭕ Burbuja", "🔺 Estrella / Polígono", "🧹 Borrador"])
with c2:
    color = st.color_picker("Tinta:", "#000000")
with c3:
    relleno = st.checkbox("Relleno", value=False)
with c4:
    grosor = st.slider("Calibre:", 2, 30, 6)
st.markdown('</div>', unsafe_allow_html=True)

if "Pincel" in trazo:
    modo = "freedraw"
    tinta = color
elif "Recto" in trazo:
    modo = "line"
    tinta = color
elif "Recuadro" in trazo:
    modo = "rect"
    tinta = color
elif "Burbuja" in trazo:
    modo = "circle"
    tinta = color
elif "Estrella" in trazo:
    modo = "polygon"
    tinta = color
else:
    modo = "freedraw"
    tinta = "#ffffff"

color_fill = color + "66" if (relleno and "Borrador" not in trazo) else "rgba(0,0,0,0)"

canvas_data = st_canvas(
    fill_color=color_fill,
    stroke_width=grosor,
    stroke_color=tinta,
    background_color="#ffffff",
    height=380,
    width=720,
    drawing_mode=modo,
    key=f"cuento_canvas_v{st.session_state.story_ver}",
)

st.write("")
b1, b2 = st.columns([3, 1])
with b1:
    btn_crear = st.button("Crear cuento a partir del dibujo", type="primary", use_container_width=True)
with b2:
    btn_limpiar = st.button("Limpiar dibujo", type="secondary", use_container_width=True)

if btn_limpiar:
    st.session_state.story_ver += 1
    if "cuento_generado" in st.session_state:
        del st.session_state.cuento_generado
    st.rerun()

def codificar_imagen(arr_data):
    img = Image.fromarray(arr_data.astype('uint8')).convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

if btn_crear:
    key_val = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key_val:
        st.warning("Configura tu clave de API en la variable OPENAI_API_KEY para redactar la historia.")
    elif canvas_data.image_data is None or not np.any(canvas_data.image_data[:, :, :3] < 250):
        st.warning("Dibuja una figura antes de solicitar el cuento.")
    else:
        prog = st.progress(0, text="Identificando personajes en el dibujo...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key_val)
            prog.progress(40, text="Escribiendo historia infantil...")
            b64 = codificar_imagen(np.array(canvas_data.image_data)[:, :, :3])

            prompt = (
                "Observa atentamente este dibujo infantil. Identifica con precisión qué personajes u objetos aparecen "
                "y escribe un cuento infantil breve, dulce y original en español en el que esos elementos sean los protagonistas. "
                "Incluye un título destacado al principio."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}],
                max_tokens=600
            )
            prog.progress(100, text="Cuento completado.")
            st.session_state.cuento_generado = resp.choices[0].message.content
        except Exception as e:
            st.error(f"Error al generar el cuento: {e}")

if "cuento_generado" in st.session_state:
    st.markdown(f'<div class="storybook-card">{st.session_state.cuento_generado}</div>', unsafe_allow_html=True)
