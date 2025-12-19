# 🔥 Sistema IoT para Detección de Incendios con Inteligencia Artificial

Proyecto Final del curso **Internet de las Cosas (IoT)**  
Universidad Nacional de San Agustín – UNSA  

Docente: **P. Maldonado Quispe (pmaldonado@unsa.edu.pe)**  
Fecha: **Diciembre 2025**

---

## 📌 Descripción General

Este proyecto consiste en el diseño e implementación de un **sistema IoT híbrido para la detección temprana de incendios**, integrando eventos generados por sensores físicos, captura de información multimedia desde un dispositivo móvil y procesamiento inteligente mediante modelos de **Deep Learning**.

El sistema busca **mejorar la precisión de detección** y **reducir falsos positivos**, combinando múltiples fuentes de información y presentando los resultados en un **dashboard web en tiempo casi real**.

---

## 🎯 Objetivo General

Construir un sistema IoT capaz de identificar un posible foco de fuego mediante la combinación de:

- Sensores físicos del entorno (temperatura, luz, entre otros)
- Captura de imágenes desde un smartphone
- Procesamiento inteligente en un backend centralizado
- Clasificación automática del evento como:
  - **NORMAL**
  - **RIESGO**
  - **CONFIRMADO**

---

## 🔄 Flujo General del Sistema

El sistema sigue el siguiente flujo de funcionamiento:

Sensores IoT / Smartphone  
↓  
MQTT (HiveMQ – mensajería asíncrona)  
↓  
Backend IoT (FastAPI + Inteligencia Artificial)  
↓  
Análisis con Deep Learning  
↓  
Dashboard Web (visualización y supervisión)

Este diseño desacoplado permite separar la comunicación IoT en tiempo real de la visualización de resultados, facilitando escalabilidad y mantenimiento.

---

## 🏗️ Arquitectura del Sistema

La arquitectura implementada se basa en un modelo cliente-servidor orientado a eventos, donde:

- Los **dispositivos IoT** generan eventos cuando se superan umbrales configurables.
- La comunicación se realiza mediante **MQTT**, optimizado para IoT.
- El **backend** procesa los eventos, descarga imágenes desde almacenamiento en la nube y ejecuta inferencia con un modelo de IA.
- El **dashboard web** consume los resultados a través de endpoints REST para su visualización.

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

🔌 Endpoints REST Utilizados

El sistema expone endpoints REST que permiten verificar el estado del backend y consultar los resultados del modelo de inteligencia artificial, los cuales son utilizados tanto por el flujo IoT como por el dashboard web.

GET /health

Este endpoint permite verificar el estado del backend IoT y confirmar que el servicio se encuentra operativo y disponible para recibir eventos.

POST /predict

Este endpoint permite ejecutar la inferencia del modelo de inteligencia artificial sobre una imagen capturada por el sistema.

Request (JSON):
```json
{
  "image_blob": "test.jpeg",
  "use_latest_if_missing": false
}
```
