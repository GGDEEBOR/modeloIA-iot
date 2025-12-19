import ssl
import threading
import json
from pathlib import Path

import paho.mqtt.client as mqtt

from app.settings import settings
from app.container import svc
from app.image_downloader import ImageDownloader  # 👈 NUEVO


# Inicializamos el downloader (una sola vez)
downloader = ImageDownloader(output_dir="downloaded_images")


def on_connect(client, userdata, flags, rc):
    print(" Conectado a HiveMQ, código:", rc)
    client.subscribe(settings.MQTT_TOPIC)
    print(f" Escuchando topic: {settings.MQTT_TOPIC}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    print("📩 Mensaje MQTT recibido:", payload)

    # --- Validar JSON ---
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("⚠️ Payload MQTT no es JSON válido:", payload)
        return

    # --- Extraer nombre del blob ---
    image_blob = data.get("photo")
    if not image_blob:
        print("⚠️ Mensaje MQTT sin campo 'photo'")
        return

    print(f"📸 Imagen recibida por MQTT (GCS): {image_blob}")

    # --- Descargar imagen de GCS ---
    try:
        local_image_path = downloader.download(image_blob)
        print(f"📥 Imagen descargada en local: {local_image_path}")
    except Exception as e:
        print(f"❌ Error descargando imagen desde GCS: {e}")
        return

    # --- Inferencia IA (pipeline original intacto) ---
    try:
        result = svc.predict_from_gcs(
            image_blob=image_blob,
            use_latest_if_missing=False
        )
        print("🔥 Resultado IA:", result.status, f"{result.final_score:.3f}")

    except Exception as e:
        print("❌ Error durante inferencia:", e)


def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
    client.loop_forever()


def start_mqtt_thread():
    threading.Thread(target=start_mqtt, daemon=True).start()
