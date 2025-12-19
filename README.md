# 🔥 Sistema IoT para Detección de Incendios con Inteligencia Artificial

Proyecto final del curso **Internet de las Cosas (IoT)**  
Universidad Nacional de San Agustín – UNSA  

Docente: **P. Maldonado Quispe**  
Fecha: **Diciembre 2025**

---

## 📌 Descripción General

Este proyecto implementa un **sistema IoT híbrido** orientado a la detección temprana de incendios, combinando:

- Eventos generados por dispositivos IoT (sensores físicos y triggers)
- Captura de imágenes desde un dispositivo móvil
- Procesamiento mediante **Inteligencia Artificial (Deep Learning)**
- Visualización de resultados en un **dashboard web en tiempo real**

El objetivo principal es **mejorar la precisión de detección** y **reducir falsos positivos** mediante la fusión de múltiples fuentes de información.

---

## 🎯 Objetivo del Proyecto

Construir un sistema IoT capaz de identificar un posible foco de fuego mediante:

- Sensores físicos (temperatura, luz, etc.) – *dispositivo IoT*
- Cámara de un smartphone (captura de imágenes)
- Procesamiento inteligente en un backend centralizado
- Clasificación del evento como:
  - **NORMAL**
  - **RIESGO**
  - **CONFIRMADO**

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura desacoplada basada en eventos:

