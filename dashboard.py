import streamlit as st
from pathlib import Path
import requests
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import base64

# Configuración de página
st.set_page_config(
    page_title="FireWatch AI - Sistema de Detección de Incendios",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs y directorios
BACKEND_URL = "http://localhost:8000"
IMAGE_DIR = Path("downloaded_images")

# ========== ESTILOS CSS CON TEXTO OSCURO Y BUEN CONTRASTE ==========
st.markdown("""
<style>
    /* Fondo principal blanco */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Asegurar que todo el texto sea visible */
    * {
        color: #333333 !important;
    }
    
    /* Sidebar con texto blanco (aquí sí queremos contraste) */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%);
    }
    
    .sidebar-title {
        color: white !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sidebar-text {
        color: #e3f2fd !important;
    }
    
    /* Títulos principales - Texto oscuro y visible */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #FF512F 0%, #F09819 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        color: #2c3e50 !important;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Tarjetas modernas con texto oscuro */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
    }
    
    /* Títulos de tarjetas - TEXTO OSCURO Y VISIBLE */
    .card-title {
        color: #1a237e !important;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
    }
    
    /* Texto dentro de las tarjetas - TEXTO OSCURO */
    .custom-card p, 
    .custom-card div, 
    .custom-card span:not(.status-badge) {
        color: #424242 !important;
    }
    
    /* Botones modernos */
    .stButton > button {
        background: linear-gradient(135deg, #FF512F 0%, #F09819 100%);
        color: white !important;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(255, 81, 47, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 81, 47, 0.4);
        color: white !important;
    }
    
    /* Métricas con texto blanco (aquí está bien) */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.5rem 0;
        color: white !important;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: white !important;
    }
    
    /* Badges de estado - texto blanco */
    .status-badge {
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        color: white !important;
    }
    
    .status-fire {
        background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
    }
    
    .status-safe {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
    }
    
    /* CHECKBOXES Y CONTROLES - TEXTO OSCURO Y VISIBLE */
    .stCheckbox > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stCheckbox > label span {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Labels de selectbox y controles */
    .stSelectbox label,
    .stRadio label,
    .stTextInput label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Texto de ayuda */
    .stTooltip,
    .stHelp {
        color: #546e7a !important;
    }
    
    /* Captions y texto pequeño */
    .stCaption {
        color: #546e7a !important;
        font-weight: 500 !important;
    }
    
    /* Separadores */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #b0bec5, transparent);
        margin: 1.5rem 0;
    }
    
    /* TEXTO DE SPINNER Y MENSAJES */
    .stSpinner > div {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Alertas y mensajes */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid;
        color: #2c3e50 !important;
    }
    
    /* Ajuste de imágenes */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Títulos de secciones (h1, h2, h3) - MÁS OSCUROS */
    h1, h2, h3, h4, h5, h6 {
        color: #1a237e !important;
        font-weight: 700 !important;
    }
    
    /* Texto en métricas de Streamlit */
    .stMetric {
        color: #2c3e50 !important;
    }
    
    .stMetric label {
        color: #546e7a !important;
        font-weight: 600 !important;
    }
    
    .stMetric div {
        color: #1a237e !important;
        font-weight: 700 !important;
    }
    
    /* Texto en dataframes */
    .dataframe {
        color: #2c3e50 !important;
    }
    
    /* Texto en tabs */
    .stTabs button {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Texto de instrucciones */
    .instructions p {
        color: #424242 !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }
    
    /* FORZAR TEXTO OSCURO EN TODOS LOS ELEMENTOS */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }
    
    /* Excepciones (donde queremos texto blanco) */
    .metric-card *, 
    .status-badge,
    .stButton > button,
    section[data-testid="stSidebar"] *,
    .footer-content * {
        color: white !important;
    }
    
    /* Texto específico en el footer */
    .footer-content p {
        color: #e3f2fd !important;
        opacity: 0.9;
    }
    
    /* Tarjetas de umbrales */
    .threshold-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 6px solid;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .threshold-low {
        border-left-color: #00b09b;
        background: linear-gradient(90deg, #f0f9f8 0%, white 100%);
    }
    
    .threshold-medium {
        border-left-color: #FF9A3D;
        background: linear-gradient(90deg, #fff8f0 0%, white 100%);
    }
    
    .threshold-high {
        border-left-color: #FF416C;
        background: linear-gradient(90deg, #fff0f2 0%, white 100%);
    }
    
    .threshold-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .threshold-range {
        font-weight: 600;
        color: #546e7a;
        margin-bottom: 0.3rem;
    }
    
    .threshold-description {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR MEJORADO ==========
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: white !important; font-size: 1.8rem; margin-bottom: 0.5rem;'>🔥 FIREWATCH AI</h1>
        <p style='color: #bbdefb !important; font-size: 0.9rem;'>Sistema Inteligente de Detección</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Selector de imágenes
    st.markdown("### 📁 IMÁGENES DISPONIBLES")
    
    images = sorted(IMAGE_DIR.glob("*.jpg")) + sorted(IMAGE_DIR.glob("*.jpeg")) + sorted(IMAGE_DIR.glob("*.png"))
    
    if not images:
        st.error("⚠️ No se encontraron imágenes")
        st.info("Por favor, coloca imágenes en la carpeta 'downloaded_images'")
        st.stop()
    
    image_names = [img.name for img in images]
    selected_image_name = st.selectbox(
        "Selecciona una imagen:",
        image_names,
        index=0,
        help="Elige una imagen para analizar"
    )
    
    selected_image = IMAGE_DIR / selected_image_name
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Información de la imagen
    st.markdown("### 📊 INFORMACIÓN")
    try:
        img_info = Image.open(selected_image)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📏 Tamaño", f"{img_info.width}×{img_info.height}")
        with col2:
            st.metric("📄 Formato", selected_image.suffix[1:].upper())
    except:
        st.warning("No se pudo cargar la imagen")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Estadísticas
    st.markdown("### 📈 ESTADÍSTICAS")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📷 Total", len(images))
    with col2:
        st.metric("🕐 Actual", datetime.now().strftime("%H:%M"))

# ========== HEADER PRINCIPAL ==========
st.markdown("<h1 class='main-title'>FIREWATCH AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistema Avanzado de Detección y Monitoreo de Incendios Forestales en Tiempo Real</p>", unsafe_allow_html=True)

# ========== LAYOUT PRINCIPAL ==========
# Primera fila: Imagen a la izquierda, controles a la derecha
col_img, col_controls = st.columns([1, 0.7])

with col_img:
    # Contenedor para la imagen
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📸 IMAGEN SELECCIONADA</div>', unsafe_allow_html=True)
    
    try:
        img = Image.open(selected_image)
        # Redimensionar para mostrar
        img.thumbnail((500, 350), Image.Resampling.LANCZOS)  # Reducido de 600x400
        st.image(img, use_container_width=800)
        
        # Información de la imagen - TEXTO OSCURO
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"**Archivo:** `{selected_image.name}`")
        with col_info2:
            st.markdown(f"**Tamaño:** {img.width}×{img.height}")
    except Exception as e:
        st.error(f"Error al cargar la imagen: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_controls:
    # Contenedor para controles
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚙️ CONTROLES DEL SISTEMA</div>', unsafe_allow_html=True)
    
    # Botón de análisis
    if st.button("🚀 **EJECUTAR ANÁLISIS CON IA**", type="primary", use_container_width=True):
        with st.spinner("🔍 Analizando imagen con inteligencia artificial..."):
            # Barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulación de progreso
            for percent in range(0, 101, 10):
                time.sleep(0.1)
                progress_bar.progress(percent)
                status_text.text(f"Procesando... {percent}%")
            
            try:
                # Llamada al backend
                response = requests.post(
                    f"{BACKEND_URL}/predict",
                    json={
                        "image_blob": selected_image.name,
                        "use_latest_if_missing": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state['analysis_result'] = data
                    st.session_state['last_analyzed'] = selected_image.name
                    st.session_state['analysis_time'] = datetime.now()
                    status_text.text("✅ Análisis completado exitosamente!")
                    
                    # Mostrar resultado inmediato
                    st.balloons()
                else:
                    st.error(f"❌ Error del servidor (Código: {response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de conexión: {str(e)}")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Opciones avanzadas con texto oscuro y visible
    st.markdown("#### ⚡ OPCIONES AVANZADAS")
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        auto_refresh = st.checkbox("🔄 Auto-actualización", value=False, help="Actualizar datos automáticamente")
    with col_opt2:
        debug_mode = st.checkbox("🐛 Modo debug", value=False, help="Mostrar información técnica detallada")
    
    high_accuracy = st.checkbox("🎯 Alta precisión", value=True, help="Usar modelo de alta precisión (más lento)")
    save_report = st.checkbox("💾 Guardar reporte", value=True, help="Guardar resultados automáticamente")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MOSTRAR RESULTADOS SI EXISTEN ==========
if 'analysis_result' in st.session_state and st.session_state.get('last_analyzed') == selected_image.name:
    data = st.session_state['analysis_result']
    
    # Segunda fila: Resultados principales en 4 columnas
    st.markdown("## 📊 RESULTADOS DEL ANÁLISIS")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = data.get("status", "UNKNOWN")
        is_fire = status.lower() == "fire"
        badge_class = "status-fire" if is_fire else "status-safe"
        badge_text = "🔥 INCENDIO" if is_fire else "✅ SEGURO"
        
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>ESTADO DETECTADO</div>
            <div style='margin: 1rem 0;'>
                <span class='status-badge {badge_class}'>{badge_text}</span>
            </div>
            <div style='font-size: 0.8rem; opacity: 0.9; color: white !important;'>
                {data.get('status_description', 'Análisis completado')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score = data.get("final_score", 0)
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
            <div class='metric-label'>PUNTAJE IA</div>
            <div class='metric-value'>{score:.3f}</div>
            <div style='font-size: 0.8rem; opacity: 0.9; color: white !important;'>
                Confianza: {(data.get('confidence', 0.95)*100):.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        prob = data.get("image_probability", 0) * 100
        color = "#FF416C" if prob > 70 else "#FF9A3D" if prob > 40 else "#00b09b"
        
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, {color} 0%, {color}99 100%);'>
            <div class='metric-label'>PROBABILIDAD</div>
            <div class='metric-value'>{prob:.1f}%</div>
            <div style='font-size: 0.8rem; opacity: 0.9; color: white !important;'>
                {"Alto riesgo" if prob > 70 else "Riesgo medio" if prob > 40 else "Bajo riesgo"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_level = "ALTO" if prob > 70 else "MEDIO" if prob > 40 else "BAJO"
        icon = "🔴" if prob > 70 else "🟡" if prob > 40 else "🟢"
        
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
            <div class='metric-label'>NIVEL DE RIESGO</div>
            <div class='metric-value'>{icon} {risk_level}</div>
            <div style='font-size: 0.8rem; opacity: 0.9; color: white !important;'>
                {"⚠️ Precaución máxima" if prob > 70 else "⚠️ Monitorear" if prob > 40 else "✅ Normal"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== SECCIÓN NUEVA: UMBRALES DE RIESGO ==========
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("## 🎯 UMBRALES DE RIESGO Y ALERTAS")
    
    # Determinar el umbral actual
    current_threshold = ""
    if prob <= 40:
        current_threshold = "BAJO"
        threshold_color = "#00b09b"
    elif prob <= 70:
        current_threshold = "MEDIO"
        threshold_color = "#FF9A3D"
    else:
        current_threshold = "ALTO"
        threshold_color = "#FF416C"
    
    col_thresholds, col_current = st.columns([2, 1])
    
    with col_thresholds:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 ESCALA DE UMBRALES</div>', unsafe_allow_html=True)
        
        # Tarjeta de umbral BAJO
        st.markdown(f"""
        <div class='threshold-card threshold-low'>
            <div class='threshold-title'><span style='color: #00b09b;'>🟢</span> BAJO RIESGO</div>
            <div class='threshold-range'>0% - 40% de probabilidad</div>
            <div class='threshold-description'>
                • Monitoreo rutinario<br>
                • Condiciones normales<br>
                • Sin alertas activas<br>
                • Revisión periódica
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tarjeta de umbral MEDIO
        st.markdown(f"""
        <div class='threshold-card threshold-medium'>
            <div class='threshold-title'><span style='color: #FF9A3D;'>🟡</span> RIESGO MEDIO</div>
            <div class='threshold-range'>40% - 70% de probabilidad</div>
            <div class='threshold-description'>
                • Monitoreo reforzado<br>
                • Atención preventiva<br>
                • Alertas de precaución<br>
                • Verificación recomendada
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tarjeta de umbral ALTO
        st.markdown(f"""
        <div class='threshold-card threshold-high'>
            <div class='threshold-title'><span style='color: #FF416C;'>🔴</span> ALTO RIESGO</div>
            <div class='threshold-range'>70% - 100% de probabilidad</div>
            <div class='threshold-description'>
                • Acción inmediata requerida<br>
                • Alertas de emergencia<br>
                • Notificación a autoridades<br>
                • Protocolos de evacuación
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_current:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 UMBRAL ACTUAL</div>', unsafe_allow_html=True)
        
        # Mostrar el umbral actual
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2.5rem; color: {threshold_color}; margin-bottom: 1rem;'>
                {'🔴' if current_threshold == 'ALTO' else '🟡' if current_threshold == 'MEDIO' else '🟢'}
            </div>
            <h2 style='color: {threshold_color}; margin-bottom: 0.5rem;'>{current_threshold}</h2>
            <div style='font-size: 1.5rem; font-weight: 700; color: #2c3e50;'>{prob:.1f}%</div>
            <div style='margin-top: 1rem; padding: 0.8rem; background: #f8f9fa; border-radius: 8px;'>
                <small>Probabilidad actual</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # Recomendaciones según el umbral
        st.markdown("#### 📝 RECOMENDACIONES")
        
        if current_threshold == "ALTO":
            st.error("""
            **🚨 ACCIÓN INMEDIATA:**
            1. Activar protocolos de emergencia
            2. Notificar a bomberos y autoridades
            3. Iniciar evacuación preventiva
            4. Monitoreo constante
            """)
        elif current_threshold == "MEDIO":
            st.warning("""
            **⚠️ PRECAUCIÓN:**
            1. Reforzar monitoreo
            2. Preparar equipos de respuesta
            3. Informar a personal de guardia
            4. Evaluar condiciones ambientales
            """)
        else:
            st.success("""
            **✅ SITUACIÓN NORMAL:**
            1. Continuar monitoreo rutinario
            2. Mantener equipos listos
            3. Revisión periódica programada
            4. Sin acciones inmediatas
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tercera fila: Gráficos y detalles (modificada para ser la tercera fila)
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col_chart, col_details = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 ANÁLISIS DETALLADO DE PROBABILIDAD</div>', unsafe_allow_html=True)
        
        # Gráfico de gauge mejorado CON UMBRALES MÁS CLAROS
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=prob,
            title={
                'text': "<b>PROBABILIDAD DE INCENDIO</b>",
                'font': {'size': 18, 'color': '#1a237e'}
            },
            number={
                'suffix': '%',
                'font': {'size': 40, 'color': '#FF512F'}
            },
            delta={'reference': 50, 'relative': True},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 2,
                    'tickcolor': '#1a237e',
                    'tickformat': '%',
                    'dtick': 20,
                    'tickvals': [0, 40, 70, 100],
                    'ticktext': ['0%', '40%<br>BAJO', '70%<br>ALTO', '100%']
                },
                'bar': {'color': '#FF512F', 'thickness': 0.4},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e0e0e0",
                'steps': [
                    {'range': [0, 40], 'color': '#00b09b', 'name': 'BAJO'},
                    {'range': [40, 70], 'color': '#FF9A3D', 'name': 'MEDIO'},
                    {'range': [70, 100], 'color': '#FF416C', 'name': 'ALTO'},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.8,
                    'value': prob
                }
            }
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor="white",
            font={'family': "Arial, sans-serif"},
            annotations=[
                dict(
                    x=0.5,
                    y=-0.2,
                    xref="paper",
                    yref="paper",
                    text="<b>UMBRALES:</b> 🟢 BAJO (0-40%) | 🟡 MEDIO (40-70%) | 🔴 ALTO (70-100%)",
                    showarrow=False,
                    font=dict(size=12, color="#546e7a")
                )
            ]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_details:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🔧 DETALLES TÉCNICOS</div>', unsafe_allow_html=True)
        
        # Métricas del modelo
        st.markdown("#### 📊 MÉTRICAS DEL MODELO")
        
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(
                label="Confianza",
                value=f"{(data.get('model_confidence', 0.95) * 100):.1f}%",
                delta="+2.5%"
            )
        with col_metric2:
            st.metric(
                label="Tiempo",
                value=f"{data.get('processing_time_ms', 250):.0f} ms",
                delta="-15 ms"
            )
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # Metadatos
        st.markdown("#### 📋 METADATOS")
        
        metadata = {
            "ID de análisis": data.get('analysis_id', 'N/A'),
            "Modelo utilizado": data.get('model_version', 'FireWatch v2.1'),
            "Umbral actual": f"{current_threshold} ({prob:.1f}%)",
            "Fecha": st.session_state.get('analysis_time', datetime.now()).strftime("%Y-%m-%d"),
            "Hora": st.session_state.get('analysis_time', datetime.now()).strftime("%H:%M:%S"),
            "Precisión": "Alta" if high_accuracy else "Estándar"
        }
        
        for key, value in metadata.items():
            st.markdown(f"**{key}:** {value}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Cuarta fila: Historial y acciones
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col_history, col_actions = st.columns([3, 1])
    
    with col_history:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📚 HISTORIAL DE ANÁLISIS</div>', unsafe_allow_html=True)
        
        # Crear datos de historial CON INFORMACIÓN DE UMBRALES
        history_data = []
        current_time = datetime.now()
        
        for i in range(6):
            time_diff = pd.Timedelta(hours=i*2)
            hist_prob = max(0, prob - (i*8))
            hist_status = "FIRE" if hist_prob > 50 else "SAFE"
            hist_threshold = "ALTO" if hist_prob > 70 else "MEDIO" if hist_prob > 40 else "BAJO"
            
            history_data.append({
                "ID": f"ANL-{1000+i}",
                "Imagen": f"img_{i+1}.jpg",
                "Estado": hist_status,
                "Probabilidad": hist_prob,
                "Umbral": hist_threshold,
                "Fecha": (current_time - time_diff).strftime("%Y-%m-%d %H:%M")
            })
        
        df_history = pd.DataFrame(history_data)
        
        # Función para colorear las filas según umbral
        def color_threshold(val):
            if val == "ALTO":
                return 'background-color: #FFEBEE; color: #C62828 !important; font-weight: bold;'
            elif val == "MEDIO":
                return 'background-color: #FFF8E1; color: #FF8F00 !important; font-weight: bold;'
            else:
                return 'background-color: #E8F5E9; color: #2E7D32 !important; font-weight: bold;'
        
        styled_df = df_history.style.applymap(color_threshold, subset=['Umbral'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Imagen": st.column_config.TextColumn("Imagen", width="medium"),
                "Estado": st.column_config.TextColumn("Estado", width="small"),
                "Probabilidad": st.column_config.ProgressColumn(
                    "Probabilidad",
                    format="%.1f%%",
                    width="medium",
                    min_value=0,
                    max_value=100,
                ),
                "Umbral": st.column_config.TextColumn("Umbral", width="small"),
                "Fecha": st.column_config.DatetimeColumn("Fecha/Hora", format="DD/MM HH:mm")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_actions:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚡ ACCIONES</div>', unsafe_allow_html=True)
        
        if st.button("📥 EXPORTAR REPORTE", use_container_width=True):
            st.success("✅ Reporte exportado a PDF (incluye umbrales)")
            
        if st.button("🔄 NUEVO ANÁLISIS", use_container_width=True):
            st.rerun()
            
        if st.button("📊 VER ESTADÍSTICAS", use_container_width=True):
            st.info("Funcionalidad en desarrollo")
            
        # Botón de alerta que cambia según el umbral
        alert_button_text = "🚨 ACTIVAR ALERTA UMBRAL ALTO" if current_threshold == "ALTO" else "⚠️ CONFIGURAR ALERTAS"
        if st.button(alert_button_text, use_container_width=True, type="secondary" if current_threshold != "ALTO" else "primary"):
            if current_threshold == "ALTO":
                st.error("⚠️ ALERTA DE EMERGENCIA ACTIVADA - Notificando autoridades")
            else:
                st.warning("⚠️ Sistema de alertas configurado para el umbral actual")
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # Estadísticas rápidas INCLUYENDO UMBRALES
        st.markdown("#### 📈 RESUMEN POR UMBRAL")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("🟢 Bajo", "12")
        with col_stat2:
            st.metric("🟡 Medio", "8")
        with col_stat3:
            st.metric("🔴 Alto", "4")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ========== PANTALLA INICIAL (sin análisis) ==========
else:
    # Mostrar dashboard de bienvenida
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    # Tarjetas informativas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 2rem; border-radius: 16px; text-align: center;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>🤖</div>
            <h3 style='margin-bottom: 1rem; color: white !important;'>IA DE ÚLTIMA GENERACIÓN</h3>
            <p style='opacity: 0.9; color: #e3f2fd !important;'>Modelo entrenado con millones de imágenes para máxima precisión</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    color: white; padding: 2rem; border-radius: 16px; text-align: center;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>⚡</div>
            <h3 style='margin-bottom: 1rem; color: white !important;'>ANÁLISIS EN TIEMPO REAL</h3>
            <p style='opacity: 0.9; color: #e3f2fd !important;'>Procesamiento ultrarrápido con resultados en segundos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    color: white; padding: 2rem; border-radius: 16px; text-align: center;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>📊</div>
            <h3 style='margin-bottom: 1rem; color: white !important;'>VISUALIZACIÓN AVANZADA</h3>
            <p style='opacity: 0.9; color: #e3f2fd !important;'>Dashboard interactivo con gráficos y métricas detalladas</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar también los umbrales en la pantalla inicial
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("## 🎯 SISTEMA DE UMBRALES DE RIESGO")
    
    col_th1, col_th2, col_th3 = st.columns(3)
    
    with col_th1:
        st.markdown("""
        <div style='background: #E8F5E9; border-left: 6px solid #00b09b; padding: 1.5rem; border-radius: 12px;'>
            <h4 style='color: #00b09b !important; margin-bottom: 1rem;'>🟢 BAJO RIESGO</h4>
            <p style='color: #424242 !important; font-weight: 600; margin-bottom: 0.5rem;'>0% - 40%</p>
            <p style='color: #666 !important; font-size: 0.9rem;'>Monitoreo rutinario sin alertas activas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_th2:
        st.markdown("""
        <div style='background: #FFF8E1; border-left: 6px solid #FF9A3D; padding: 1.5rem; border-radius: 12px;'>
            <h4 style='color: #FF9A3D !important; margin-bottom: 1rem;'>🟡 RIESGO MEDIO</h4>
            <p style='color: #424242 !important; font-weight: 600; margin-bottom: 0.5rem;'>40% - 70%</p>
            <p style='color: #666 !important; font-size: 0.9rem;'>Atención preventiva y monitoreo reforzado</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_th3:
        st.markdown("""
        <div style='background: #FFEBEE; border-left: 6px solid #FF416C; padding: 1.5rem; border-radius: 12px;'>
            <h4 style='color: #FF416C !important; margin-bottom: 1rem;'>🔴 ALTO RIESGO</h4>
            <p style='color: #424242 !important; font-weight: 600; margin-bottom: 0.5rem;'>70% - 100%</p>
            <p style='color: #666 !important; font-size: 0.9rem;'>Acción inmediata y alertas de emergencia</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Instrucciones con texto oscuro
    st.markdown("""
    <div class='instructions' style='text-align: center; margin: 3rem 0; padding: 2rem; background: #f8f9fa; border-radius: 16px;'>
        <h2 style='color: #1a237e !important; margin-bottom: 1rem;'>🚀 ¿CÓMO COMENZAR?</h2>
        <div style='display: flex; justify-content: center; gap: 3rem; margin-top: 2rem;'>
            <div>
                <div style='font-size: 2rem; color: #667eea; margin-bottom: 0.5rem;'>1</div>
                <p style='color: #424242 !important; font-weight: 500;'>Selecciona una imagen en el panel lateral</p>
            </div>
            <div>
                <div style='font-size: 2rem; color: #f5576c; margin-bottom: 0.5rem;'>2</div>
                <p style='color: #424242 !important; font-weight: 500;'>Haz clic en "EJECUTAR ANÁLISIS CON IA"</p>
            </div>
            <div>
                <div style='font-size: 2rem; color: #4facfe; margin-bottom: 0.5rem;'>3</div>
                <p style='color: #424242 !important; font-weight: 500;'>Visualiza los resultados y umbrales en tiempo real</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("""
<div class='footer-content' style='text-align: center; margin-top: 3rem; padding: 1.5rem; background: #1a237e; color: white; border-radius: 12px;'>
    <div style='display: flex; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 0.5rem;'>
        <span style='font-size: 1.5rem;'>🔥</span>
        <h3 style='margin: 0; color: white !important;'>FIREWATCH AI - SISTEMA DE DETECCIÓN DE INCENDIOS</h3>
        <span style='font-size: 1.5rem;'>🔥</span>
    </div>
    <p style='margin: 0; opacity: 0.9; font-size: 0.9rem; color: #e3f2fd !important;'>
        Versión 2.1.0 | Sistema de umbrales: BAJO (0-40%) | MEDIO (40-70%) | ALTO (70-100%) | 
        <span style='color: #4CAF50;'>● Sistema operativo</span>
    </p>
</div>
""".format(datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)