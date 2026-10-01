import os
import streamlit as st
import streamlit.components.v1 as components
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
# CONFIGURACIÓN Y MOTOR VISUAL NOIR
# -----------------------------------------------------------------------------
st.set_page_config(page_title='Tablero Inteligente', layout='wide')

# 1. Inyección de Javascript en el documento padre (Estela del mouse + Foco ambiental)
components.html(
    """
    <script>
    const parentDoc = window.parent.document;
    
    // Evitar inyecciones duplicadas al refrescar
    if (!parentDoc.getElementById('noir-fx-canvas')) {
        // Lienzo para partículas del mouse
        const canvas = parentDoc.createElement('canvas');
        canvas.id = 'noir-fx-canvas';
        canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:999999;';
        parentDoc.body.appendChild(canvas);

        // Foco de luz sutil que sigue al cursor
        const torch = parentDoc.createElement('div');
        torch.id = 'noir-torch';
        torch.style.cssText = 'position:fixed;top:0;left:0;width:500px;height:500px;border-radius:50%;background:radial-gradient(circle, rgba(255,255,255,0.035) 0%, rgba(255,255,255,0) 70%);pointer-events:none;transform:translate(-50%, -50%);z-index:1;transition:opacity 0.3s;';
        parentDoc.body.appendChild(torch);

        const ctx = canvas.getContext('2d');
        let width = canvas.width = window.parent.innerWidth;
        let height = canvas.height = window.parent.innerHeight;

        window.parent.addEventListener('resize', () => {
            width = canvas.width = window.parent.innerWidth;
            height = canvas.height = window.parent.innerHeight;
        });

        const points = [];
        window.parent.addEventListener('mousemove', (e) => {
            torch.style.left = e.clientX + 'px';
            torch.style.top = e.clientY + 'px';
            
            // Generar partículas en la estela
            points.push({
                x: e.clientX,
                y: e.clientY,
                alpha: 1.0,
                radius: Math.random() * 2 + 1.2,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5
            });
        });

        function render() {
            ctx.clearRect(0, 0, width, height);
            for (let i = 0; i < points.length; i++) {
                const p = points[i];
                p.x += p.vx;
                p.y += p.vy;
                p.alpha *= 0.94;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius * p.alpha, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha * 0.25})`;
                ctx.fill();
            }
            while (points.length > 0 && points[0].alpha < 0.03) {
                points.shift();
            }
            requestAnimationFrame(render);
        }
        render();
    }
    </script>
    """,
    height=0,
    width=0,
)

# 2. Hoja de Estilos Noir (Dark Obsidian, Marcos 80% y microinteracciones)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Fondo principal y limpieza de interfaz nativa */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050507 !important;
        color: #e4e4e7 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* Tipografía sobria */
    h1 {
        text-align: center;
        font-size: 1.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.16em !important;
        text-transform: uppercase !important;
        color: #fafafa !important;
        margin-top: 1rem !important;
        margin-bottom: 0.4rem !important;
    }

    h3 {
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        color: #71717a !important;
        letter-spacing: 0.05em !important;
    }

    .canvas-instruction {
        text-align: center;
        font-size: 0.82rem;
        color: #71717a;
        margin-bottom: 1.8rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Marco del Lienzo: Centrado al 80% con aura reactiva */
    .studio-frame {
        position: relative;
        background: #000000;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 6px;
        padding: 6px;
        display: flex;
        justify-content: center;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95);
        transition: border-color 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s ease;
    }

    .studio-frame:hover {
        border-color: rgba(255, 255, 255, 0.4);
        box-shadow: 0 0 35px rgba(255, 255, 255, 0.06);
    }

    div[data-testid="stCustomComponentV1"] iframe {
        border-radius: 4px !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Campos de entrada tipo consola */
    div[data-testid="stTextInput"] input {
        background-color: #0c0c0e !important;
        color: #f4f4f5 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        padding: 0.7rem 0.9rem !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255, 255, 255, 0.35) !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.05) !important;
    }

    /* Botones Monocromáticos de Alto Impacto */
    div.stButton > button {
        border-radius: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        padding: 0.8rem 1.6rem !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }

    div.stButton > button[kind="secondary"] {
        background-color: #f4f4f5 !important;
        color: #09090b !important;
        font-weight: 600 !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #ffffff !important;
        transform: translateY(-2px) scale(1.005);
        box-shadow: 0 8px 25px rgba(255, 255, 255, 0.18) !important;
    }

    /* Caja de respuesta / Consola de salida */
    div[data-testid="stMarkdownContainer"] p {
        line-height: 1.65;
        font-size: 0.98rem;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #050507 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 2.5rem 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# INTERFAZ Y FLUJO DE DATOS (LÓGICA INTACTA)
# -----------------------------------------------------------------------------
st.title('Tablero Inteligente')

with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)

# Distribución: 10% margen | 80% centro | 10% margen
col_l, col_center, col_r = st.columns([1, 8, 1])

with col_center:
    st.markdown('<div class="canvas-instruction">Dibuja el boceto en el panel y presiona el botón para analizarla</div>', unsafe_allow_html=True)

    drawing_mode = "freedraw"
    stroke_color = "#000000"
    bg_color = '#FFFFFF'

    # Contenedor estilizado para el canvas
    st.markdown('<div class="studio-frame">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

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
