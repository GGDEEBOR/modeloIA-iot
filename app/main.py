from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from app.settings import settings
from app.container import svc
from app.mqtt_listener import start_mqtt_thread

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("iot-fire-ai")

app = FastAPI(
    title="IoT Fire Multimodal Inference Service",
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    start_mqtt_thread()
    logger.info("🚀 MQTT listener iniciado")




class PredictRequest(BaseModel):
    image_blob: str | None = None
    audio_blob: str | None = None
    use_latest_if_missing: bool = True


class PredictResponse(BaseModel):
    status: str
    final_score: float
    image_probability: float
    audio_probability: float | None
    meta: dict


@app.get("/health")
def health():
    return {"ok": True, "version": app.version}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        res = svc.predict_from_gcs(
            image_blob=req.image_blob,
            audio_blob=req.audio_blob,
            use_latest_if_missing=req.use_latest_if_missing,
        )
        return PredictResponse(
            status=res.status,
            final_score=res.final_score,
            image_probability=res.image_probability,
            audio_probability=res.audio_probability,
            meta=res.meta,
        )
    except Exception as e:
        logger.exception("Error en /predict")
        raise HTTPException(status_code=400, detail=str(e))
