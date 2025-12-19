import ssl
import threading
import paho.mqtt.client as mqtt
import json
from app.inference import InferenceService
from app.settings import settings



inference_service = InferenceService()


def on_connect(client, userdata, flags, rc):
    print(" Conectado a HiveMQ, código:", rc)
    client.subscribe(settings.MQTT_TOPIC)
    print(f" Escuchando topic: {settings.MQTT_TOPIC}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        print("📩 Mensaje MQTT recibido:", payload)

        data = json.loads(payload)

        image_name = data.get("photo")
        if not image_name:
            print("⚠️ Mensaje MQTT sin campo 'photo'")
            return

        print(f"📸 Imagen recibida por MQTT: {image_name}")

        result = inference_service.predict_from_gcs(
            image_blob=image_name,
            use_latest_if_missing=False
        )

        print("🔥 Resultado IA:", result.status, result.final_score)

    except Exception as e:
        print("❌ Error procesando mensaje MQTT:", e)

def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

    client.tls_set(tls_version=ssl.PROTOCOL_TLS)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)

    client.loop_forever()


def start_mqtt_thread():
    t = threading.Thread(target=start_mqtt, daemon=True)
    t.start()
