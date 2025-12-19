# 🔥 FireWatch AI – Backend IoT e Inteligencia Artificial

Proyecto Final – Internet de las Cosas (IoT)  
Universidad Nacional de San Agustín de Arequipa (UNSA)  
Diciembre 2025  

---

## 📌 Descripción de este repositorio

Este repositorio implementa la **capa central de procesamiento inteligente del sistema FireWatch AI**, encargada de la recepción de eventos IoT, el procesamiento de información multimedia y la ejecución de inferencia mediante modelos de Inteligencia Artificial.

El módulo desarrollado integra mensajería IoT, servicios backend y visualización web, permitiendo la **detección temprana de incendios** y la clasificación automática de eventos según su nivel de riesgo.

Este repositorio corresponde **únicamente** a la capa de Backend IoT + IA del proyecto general.

---

## 🎯 Rol dentro del proyecto FireWatch AI

Este módulo se encarga específicamente de:

- Recibir eventos desde el sistema IoT mediante MQTT  
- Descargar imágenes asociadas a los eventos detectados  
- Ejecutar inferencia con un modelo de Deep Learning  
- Clasificar el evento como:
  - NORMAL
  - RIESGO
  - CONFIRMADO  
- Exponer resultados mediante endpoints REST  
- Proveer información procesada al dashboard web  

Otros componentes del sistema (firmware IoT, aplicación móvil, broker MQTT e infraestructura) se desarrollan y documentan en repositorios independientes.

---

## 🧠 Tecnologías utilizadas

- Python 3.10+
- FastAPI
- MQTT (HiveMQ)
- PyTorch
- Streamlit
- Docker
- Google Cloud Storage

---

## 📂 Estructura del Proyecto

```text
MODELOIA-IOT/
├── app/
│   ├── container.py          # Instancia global del servicio de inferencia
│   ├── gcs_client.py         # Cliente de Google Cloud Storage
│   ├── image_downloader.py   # Descarga persistente de imágenes
│   ├── image_model.py        # Modelo CNN (EfficientNet)
│   ├── inference.py          # Lógica de inferencia con IA
│   ├── main.py               # Backend FastAPI
│   ├── mqtt_listener.py      # Listener MQTT (HiveMQ)
│   └── settings.py           # Configuración general del sistema
│
├── downloaded_images/        # Imágenes descargadas y analizadas
├── models/
│   └── image_fire.pt         # Pesos del modelo entrenado
├── scripts/
│   └── train_image.py        # Script de entrenamiento del modelo
├── dashboard.py              # Dashboard web (Streamlit)
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

---

## 🔌 Endpoints REST implementados

### GET /health

Permite verificar el estado del backend IoT.

Respuesta esperada:
```json
{
  "status": "ok"
}
```


---


### POST /predict

Ejecuta la inferencia del modelo de Inteligencia Artificial sobre una imagen almacenada.

Request:
```json
{
  "image_blob": "test.jpeg",
  "use_latest_if_missing": false
}
```

Response:
```json
{
  "status": "FIRE",
  "final_score": 0.80,
  "image_probability": 1.0,
  "confidence": 0.95
}
```
Este endpoint es utilizado tanto por el flujo IoT como por el dashboard web.

---



## ▶️ Ejecución del proyecto en entorno local

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/firewatch-ai-backend.git
cd MODELOIA-IOT
```

### 2. Crear y activar entorno virtual
Crear el entorno virtual:
```bash
python -m venv venv
```
Activar el entorno virtual:

#### Windows
```bash
venv\Scripts\activate
```
#### Linux / macOS
```bash
source venv/bin/activate
```




### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```


### 4. Configurar variables de entorno
Crear el archivo .env en la raíz del proyecto con el siguiente contenido:

```bash
MQTT_BROKER_URL=broker.hivemq.com
MQTT_TOPIC=pic
GCS_BUCKET_NAME=firewatch-images
GOOGLE_APPLICATION_CREDENTIALS=secrets/service_account.json

```


### 5. Ejecutar el backend IoT

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
El backend quedará disponible en:
```bash
http://localhost:8000
```


### 6. Ejecutar el dashboard web
En una nueva terminal (con el entorno virtual activo):
```bash
streamlit run dashboard.py

```
El dashboard estará disponible en:

```bash
http://localhost:8501
```







