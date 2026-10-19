import os
import io
import base64
import numpy as np
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
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
# ESTILOS: TALLER DE FANTASÍA Y NOCHE ESTRELLADA
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&family=Spectral:ital,wght@0,500;0,700;1,400&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp, section.main, .block-container {
    background: transparent !important;
    background-color: transparent !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

body {
    background-color: #070714 !important;
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
    background: rgba(18, 14, 36, 0.92);
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

# Fondo interactivo noche estrellada animado en Canvas (Cero Lag)
components.html(
    """
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        if (pWin.__STORY_BG_INIT__) return;
        pWin.__STORY_BG_INIT__ = true;

        let canvas = pDoc.getElementById('story-fluid-canvas');
        if (!canvas) {
            canvas = pDoc.createElement('canvas');
            canvas.id = 'story-fluid-canvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;background:#070714;';
            pDoc.body.prepend(canvas);
        }

        const ctx = canvas.getContext('2d');
        let w = canvas.width = pWin.innerWidth;
        let h = canvas.height = pWin.innerHeight;

        pWin.addEventListener('resize', () => {
            w = canvas.width = pWin.innerWidth;
            h = canvas.height = pWin.innerHeight;
        });

        const orbs = [
            { x: w * 0.2, y: h * 0.25, r: 260, vx: 0.5, vy: 0.4, color: 'rgba(255, 209, 102, 0.16)' },
            { x: w * 0.8, y: h * 0.35, r: 280, vx: -0.4, vy: 0.5, color: 'rgba(6, 214, 160, 0.15)' },
            { x: w * 0.5, y: h * 0.75, r: 250, vx: 0.4, vy: -0.5, color: 'rgba(168, 85, 247, 0.14)' }
        ];

        function loop() {
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#070714';
            ctx.fillRect(0, 0, w, h);
            ctx.globalCompositeOperation = 'screen';

            for (let b of orbs) {
                b.x += b.vx;
                b.y += b.vy;
                if (b.x < -100 || b.x > w + 100) b.vx *= -1;
                if (b.y < -100 || b.y > h + 100) b.vy *= -1;

                const g = ctx.createRadialGradient(b.x, b.y, 10, b.x, b.y, b.r);
                g.addColorStop(0, b.color);
                g.addColorStop(1, 'transparent');
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.fill();
            }
            requestAnimationFrame(loop);
        }
        loop();
    })();
    </script>
    """,
    height=0,
    width=0
)

st.markdown('<div class="brand-signature">Krov Industries · Creatividad Lúdica</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Taller de Cuentos Ilustrados</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Dibuja una escena o personaje infantil y la IA redactará una historia original</div>', unsafe_allow_html=True)

# CAMPO DE CLAVE OPENAI DIRECTO EN PANTALLA
c_key, c_info = st.columns([1.5, 1])
with c_key:
    api_key_input = st.text_input(
        "Clave de API de OpenAI:",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-..."
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

# HERRAMIENTAS DIRECTAS EN COLUMNAS (SIN CONTENEDORES VACÍOS)
c1, c2, c3, c4 = st.columns([1.5, 0.9, 0.8, 1.1])
with c1:
    trazo = st.selectbox("Pincel:", ["🖍️ Pincel Mágico", "📏 Trazo Recto", "⏹️ Recuadro", "⭕ Burbuja", "🔺 Estrella / Polígono", "🧹 Borrador"])
with c2:
    color = st.color_picker("Tinta:", "#000000")
with c3:
    relleno = st.checkbox("Relleno", value=False)
with c4:
    grosor = st.slider("Calibre:", 2, 30, 6)

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
        st.warning("Introduce tu clave de API de OpenAI en el campo superior.")
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
