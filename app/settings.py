from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Server ---
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # --- Google Cloud Storage ---
    GCS_SA_JSON: str = "./secrets/service_account.json"
    GCS_BUCKET: str = "test-setup"
    GCS_IMAGE_PREFIX: str = "images/" ###
    GCS_AUDIO_PREFIX: str = "audio/"

    # --- Model ---
    IMAGE_MODEL_PATH: str = "./models/image_fire.pt"
    IMG_THRESHOLD_RISK: float = 0.40
    IMG_THRESHOLD_CONFIRM: float = 0.70

    USE_AUDIO: bool = False
    IMAGE_WEIGHT: float = 0.80
    AUDIO_WEIGHT: float = 0.20

    # --- MQTT (🔴 ESTO FALTABA) ---
    MQTT_HOST: str
    MQTT_PORT: int = 8883
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_TOPIC: str


settings = Settings()
