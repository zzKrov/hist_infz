import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

# Inicializar session_state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'full_response' not in st.session_state:
    st.session_state.full_response = ""
if 'base64_image' not in st.session_state:
    st.session_state.base64_image = ""


def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# -----------------------------------------------------------------------------
# CONFIGURACIÓN VISUAL Y ESTILOS NOIR
# -----------------------------------------------------------------------------
st.set_page_config(page_title='Tablero Inteligente', layout='wide')

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Fondo principal y tipografía sobria */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #09090b !important;
        color: #f4f4f5 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Encabezados */
    h1 {
        text-align: center;
        font-size: 1.6rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: #fafafa !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    h3 {
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        color: #a1a1aa !important;
        letter-spacing: 0.02em !important;
    }

    .canvas-instruction {
        text-align: center;
        font-size: 0.85rem;
        color: #71717a;
        margin-bottom: 1.5rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Contenedor del lienzo centrado al 80% */
    div[data-testid="stCanvas"] {
        display: flex !important;
        justify-content: center !important;
    }

    div[data-testid="stCanvas"] > canvas {
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 4px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.8) !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    }

    div[data-testid="stCanvas"] > canvas:hover {
        border-color: rgba(255, 255, 255, 0.35) !important;
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.03) !important;
    }

    /* Inputs de texto estilo estudio */
    div[data-testid="stTextInput"] input {
        background-color: #111114 !important;
        color: #f4f4f5 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 0.8rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.05) !important;
    }

    /* Botones sobrios */
    div.stButton > button {
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        padding: 0.65rem 1.4rem !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        background-color: #fafafa !important;
        color: #09090b !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button:hover {
        background-color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.15) !important;
    }

    /* Sidebar minimalista */
    section[data-testid="stSidebar"] {
        background-color: #070709 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* Línea divisoria */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 2rem 0 !important;
    }
    </style>

    <!-- Estela reactiva del cursor -->
    <canvas id="trailCanvas" style="position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:99999;"></canvas>
    <script>
    (function() {
        const doc = window.parent.document;
        let canvas = doc.getElementById('trailCanvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'trailCanvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:99999;';
            doc.body.appendChild(canvas);
        }
        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.parent.innerWidth;
        let height = canvas.height = window.parent.innerHeight;

        window.parent.addEventListener('resize', () => {
            width = canvas.width = window.parent.innerWidth;
            height = canvas.height = window.parent.innerHeight;
        });

        const points = [];
        window.parent.addEventListener('mousemove', (e) => {
            points.push({ x: e.clientX, y: e.clientY, alpha: 1.0 });
        });

        function render() {
            ctx.clearRect(0, 0, width, height);
            for (let i = 0; i < points.length; i++) {
                const pt = points[i];
                pt.alpha *= 0.93;
                ctx.beginPath();
                ctx.arc(pt.x, pt.y, (1 - (i / points.length)) * 2.2, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${pt.alpha * 0.12})`;
                ctx.fill();
            }
            while (points.length > 0 && points[0].alpha < 0.05) {
                points.shift();
            }
            requestAnimationFrame(render);
        }
        render();
    })();
    </script>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# INTERFAZ Y FLUJO DE DATOS
# -----------------------------------------------------------------------------
st.title('Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

# Distribución en columnas: 10% margen | 80% centro | 10% margen
col_l, col_center, col_r = st.columns([1, 8, 1])

with col_center:
    st.markdown('<div class="canvas-instruction">Dibuja el boceto en el panel y presiona el botón para analizarla</div>', unsafe_allow_html=True)

    drawing_mode = "freedraw"
    stroke_color = "#000000"
    bg_color = '#FFFFFF'

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=380,
        width=880,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    st.write("")
    ke = st.text_input('Ingresa tu Clave', type="password")
    os.environ['OPENAI_API_KEY'] = ke

    # Retrieve the OpenAI API Key
    api_key = os.environ['OPENAI_API_KEY']

    # Initialize the OpenAI client with the API key
    client = OpenAI(api_key=api_key)

    st.write("")
    analyze_button = st.button("Analiza la imagen", type="secondary", use_container_width=True)

    # Check if an image has been uploaded, if the API key is available, and if the button has been pressed
    if canvas_result.image_data is not None and api_key and analyze_button:

        with st.spinner("Analizando ..."):
            # Encode the image
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8')).convert('RGBA')
            input_image.save('img.png')
            
            # Codificar la imagen en base64
            base64_image = encode_image_to_base64("img.png")
            st.session_state.base64_image = base64_image
                
            prompt_text = (f"Describe in spanish briefly the image")
        
            # Make the request to the OpenAI API
            try:
                full_response = ""
                message_placeholder = st.empty()
                response = openai.chat.completions.create(
                  model="gpt-4o-mini",
                  messages=[
                    {
                       "role": "user",
                       "content": [
                         {"type": "text", "text": prompt_text},
                         {
                           "type": "image_url",
                           "image_url": {
                             "url": f"data:image/png;base64,{base64_image}",
                           },
                         },
                       ],
                      }
                    ],
                  max_tokens=500,
                  )
                
                if response.choices[0].message.content is not None:
                        full_response += response.choices[0].message.content
                        message_placeholder.markdown(full_response + "▌")
                
                # Final update to placeholder after the stream ends
                message_placeholder.markdown(full_response)
                
                # Guardar en session_state
                st.session_state.full_response = full_response
                st.session_state.analysis_done = True
                
                if Expert == profile_imgenh:
                   st.session_state.mi_respuesta = response.choices[0].message.content
        
            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Mostrar la funcionalidad de crear historia si ya se hizo el análisis
    if st.session_state.analysis_done:
        st.divider()
        st.subheader("📚 ¿Quieres crear una historia?")
        
        if st.button("✨ Crear historia infantil", use_container_width=True):
            with st.spinner("Creando historia..."):
                story_prompt = f"Basándote en esta descripción: '{st.session_state.full_response}', crea una historia infantil breve y entretenida. La historia debe ser creativa y apropiada para niños."
                
                story_response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": story_prompt}],
                    max_tokens=500,
                )
                
                st.markdown("**📖 Tu historia:**")
                st.write(story_response.choices[0].message.content)

    # Warnings for user action required
    if not api_key:
        st.warning("Por favor ingresa tu API key.")
