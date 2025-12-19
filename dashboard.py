import streamlit as st
from pathlib import Path
import requests
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuración de página
st.set_page_config(
    page_title="FireWatch AI - Detección de Incendios",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs y directorios
BACKEND_URL = "http://localhost:8000"
IMAGE_DIR = Path("downloaded_images")

# ========== ESTILOS CSS PERSONALIZADOS ==========
st.markdown("""
<style>
    /* Estilos generales */
    .main {
        padding: 1rem 2rem;
    }
    
    /* Títulos y encabezados */
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #FF4B4B, #FF9A3D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Tarjetas y contenedores */
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Métricas y KPIs */
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin: 1.5rem 0;
    }
    
    .kpi-card {
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        min-width: 150px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Badges de estado */
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .status-safe {
        background: linear-gradient(135deg, #56ab2f, #a8e063);
        color: white;
    }
    
    .status-fire {
        background: linear-gradient(135deg, #FF416C, #FF4B2B);
        color: white;
    }
    
    .status-unknown {
        background: linear-gradient(135deg, #757F9A, #D7DDE8);
        color: white;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #FF4B4B, #FF9A3D);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50, #1a1a2e);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FF4B4B, #FF9A3D);
    }
    
    /* Selectbox */
    .stSelectbox label {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .kpi-container {
            flex-direction: column;
            gap: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h2 style='color: white; margin-bottom: 0;'>🔥 FireWatch AI</h2>
        <p style='color: #aaa; font-size: 0.9rem;'>Sistema de Monitoreo Inteligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Selector de imagen con mejor diseño
    st.markdown("### 📁 Imágenes Disponibles")
    
    images = sorted(IMAGE_DIR.glob("*.jpg")) + sorted(IMAGE_DIR.glob("*.jpeg"))
    
    if not images:
        st.warning("No hay imágenes en el directorio. Por favor, sube imágenes primero.")
        st.stop()
    
    # Crear lista con nombres formateados
    image_options = [img.name for img in images]
    selected_image_name = st.selectbox(
        "Seleccionar imagen:",
        image_options,
        help="Selecciona una imagen para analizar"
    )
    
    selected_image = IMAGE_DIR / selected_image_name
    
    # Información de la imagen seleccionada
    st.markdown("---")
    st.markdown("### 📊 Información de la Imagen")
    
    try:
        img_info = Image.open(selected_image)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tamaño", f"{img_info.width}×{img_info.height}")
        with col2:
            st.metric("Formato", selected_image.suffix[1:].upper())
    except:
        st.error("Error al cargar la imagen")
    
    # Estadísticas
    st.markdown("---")
    st.markdown("### 📈 Estadísticas")
    st.metric("Total de imágenes", len(images))
    st.metric("Última actualización", datetime.now().strftime("%H:%M"))

# ========== HEADER PRINCIPAL ==========
st.markdown("<h1 class='main-title'>FireWatch AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Sistema Inteligente de Detección y Monitoreo de Incendios Forestales</p>", unsafe_allow_html=True)

# ========== LAYOUT PRINCIPAL ==========
# Tarjeta de vista previa de imagen
col_img, col_controls = st.columns([2, 1])

with col_img:
    st.markdown("### 📸 Vista Previa")
    card_img = st.container()
    with card_img:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        try:
            img = Image.open(selected_image)
            # Redimensionar manteniendo aspecto
            max_size = (600, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            st.image(img, use_container_width=True)
        except:
            st.error("No se pudo cargar la imagen")
        st.markdown(f"**Archivo:** `{selected_image.name}`", unsafe_allow_html=True)
        st.markdown(f"**Fecha de análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col_controls:
    st.markdown("### ⚙️ Controles")
    card_controls = st.container()
    with card_controls:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Botón de análisis
        if st.button("🚀 **Ejecutar Análisis IA**", type="primary", use_container_width=True):
            with st.spinner("Analizando imagen con IA..."):
                # Simular progreso
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Llamada al backend
                try:
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
                        st.success("✅ Análisis completado!")
                    else:
                        st.error(f"❌ Error del servidor: {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error de conexión: {str(e)}")
        
        st.markdown("---")
        
        # Opciones adicionales
        st.markdown("#### 🔧 Opciones Avanzadas")
        auto_refresh = st.checkbox("Actualización automática", value=False)
        show_confidence = st.checkbox("Mostrar intervalos de confianza", value=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ========== RESULTADOS DEL ANÁLISIS ==========
if 'analysis_result' in st.session_state and st.session_state.get('last_analyzed') == selected_image.name:
    data = st.session_state['analysis_result']
    
    # Tarjeta de resultados principales
    st.markdown("## 📊 Resultados del Análisis")
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = data["status"]
        status_class = "status-fire" if status.lower() == "fire" else "status-safe"
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>ESTADO</div>
            <div class='kpi-value'><span class='status-badge {status_class}'>{status.upper()}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score = data["final_score"]
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>SCORE IA</div>
            <div class='kpi-value'>{score:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        prob = data["image_probability"] * 100
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>PROBABILIDAD</div>
            <div class='kpi-value'>{prob:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_level = "ALTO" if prob > 70 else "MEDIO" if prob > 40 else "BAJO"
        risk_color = "#FF4B4B" if prob > 70 else "#FF9A3D" if prob > 40 else "#56ab2f"
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>NIVEL DE RIESGO</div>
            <div class='kpi-value' style='color: {risk_color};'>{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos y visualizaciones
    col_chart, col_details = st.columns([2, 1])
    
    with col_chart:
        st.markdown("### 📈 Análisis de Probabilidad")
        
        # Gráfico de gauge mejorado
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=prob,
            title={
                'text': "Probabilidad de Incendio",
                'font': {'size': 20, 'color': '#333'}
            },
            delta={'reference': 50},
            gauge={
                'axis': {
                    'range': [0, 100],
                    'tickwidth': 1,
                    'tickcolor': "#333",
                    'tickformat': '%'
                },
                'bar': {'color': "#FF4B4B", 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': '#56ab2f'},
                    {'range': [30, 70], 'color': '#FF9A3D'},
                    {'range': [70, 100], 'color': '#FF4B4B'},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': prob
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'color': "#333", 'family': "Arial"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_details:
        st.markdown("### 📋 Detalles Técnicos")
        
        details_card = st.container()
        with details_card:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            st.markdown("#### Métricas del Modelo")
            st.metric("Confianza del modelo", f"{(data.get('model_confidence', 0.95) * 100):.1f}%")
            st.metric("Tiempo de procesamiento", f"{data.get('processing_time_ms', 250):.0f} ms")
            
            st.markdown("---")
            
            st.markdown("#### Metadatos")
            st.text(f"ID de análisis: {data.get('analysis_id', 'N/A')}")
            st.text(f"Modelo utilizado: {data.get('model_version', 'v2.1')}")
            st.text(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabla de historial
    st.markdown("### 📚 Historial de Análisis")
    
    # Crear dataframe con datos simulados para el historial
    history_data = []
    for i in range(5):
        history_data.append({
            "ID": f"ANL-{1000+i}",
            "Imagen": selected_image.name,
            "Estado": "FIRE" if i % 2 == 0 else "SAFE",
            "Probabilidad": f"{prob - (i*5):.1f}%" if prob - (i*5) > 0 else "0.0%",
            "Score": f"{score - (i*0.05):.3f}",
            "Fecha": (datetime.now() - pd.Timedelta(hours=i)).strftime("%Y-%m-%d %H:%M")
        })
    
    df_history = pd.DataFrame(history_data)
    
    # Mostrar la tabla con columnas configuradas (corregido el uso de use_container_width)
    st.dataframe(
        df_history,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID Análisis", width="small"),
            "Imagen": st.column_config.TextColumn("Imagen", width="medium"),
            "Estado": st.column_config.TextColumn("Estado", width="small"),
            "Probabilidad": st.column_config.ProgressColumn(
                "Probabilidad",
                format="%s",
                width="medium",
                min_value=0,
                max_value=100,
            ),
            "Score": st.column_config.NumberColumn("Score IA", format="%.3f"),
            "Fecha": st.column_config.DatetimeColumn("Fecha/Hora", format="YYYY-MM-DD HH:mm")
        }
    )
    
    # Botón para exportar resultados
    col_export, col_refresh, _ = st.columns([1, 1, 2])
    with col_export:
        if st.button("📥 Exportar Reporte", use_container_width=True):
            st.success("Reporte exportado exitosamente (simulación)")
    with col_refresh:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()

# ========== MENSAJE INICIAL ==========
else:
    if 'analysis_result' not in st.session_state:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px;'>
            <h2 style='color: #333;'>🚀 Bienvenido a FireWatch AI</h2>
            <p style='color: #666; font-size: 1.1rem; margin: 1rem 0;'>
                Selecciona una imagen en el panel lateral y haz clic en <strong>"Ejecutar Análisis IA"</strong> para comenzar
            </p>
            <div style='font-size: 0.9rem; color: #888; margin-top: 2rem;'>
                <p>📊 Visualización avanzada de datos | 🤖 Modelo IA de última generación | ⚡ Análisis en tiempo real</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>🔥 <strong>FireWatch AI</strong> - Sistema de Detección de Incendios v2.1</p>
    <p style='font-size: 0.8rem;'>Última actualización: {} | Sistema operativo</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)