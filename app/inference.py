from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .settings import settings
from .gcs_client import GCSClient, GCSConfig
from .image_model import FireImageClassifier, ImageModelConfig


@dataclass
class InferenceResult:
    image_probability: float
    audio_probability: Optional[float]
    final_score: float
    status: str
    meta: Dict[str, Any]


class InferenceService:
    def __init__(self) -> None:
        # GCS client (opcional según uso)
        self.gcs = GCSClient(GCSConfig(sa_json_path=settings.GCS_SA_JSON, bucket_name=settings.GCS_BUCKET))

        # Device
        device = "cuda" if (os.getenv("CUDA_VISIBLE_DEVICES") not in [None, ""] and self._has_cuda()) else "cpu"

        self.img_model = FireImageClassifier(ImageModelConfig(
            weights_path=settings.IMAGE_MODEL_PATH,
            device=device
        ))

    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def _status_from_score(self, score: float) -> str:
        if score >= settings.IMG_THRESHOLD_CONFIRM:
            return "CONFIRMADO"
        if score >= settings.IMG_THRESHOLD_RISK:
            return "RIESGO"
        return "NORMAL"

    def predict_from_gcs(
        self,
        image_blob: Optional[str] = None,
        audio_blob: Optional[str] = None,
        use_latest_if_missing: bool = True,
    ) -> InferenceResult:
        """
        Descarga desde GCS y predice.
        - Si image_blob no viene y use_latest_if_missing=True, toma el último del prefijo images/
        """
        with tempfile.TemporaryDirectory() as tmp:
            # Resolver blob de imagen
            if not image_blob and use_latest_if_missing:
                image_blob = self.gcs.find_latest_blob(prefix=settings.GCS_IMAGE_PREFIX)

            if not image_blob:
                raise ValueError("No se encontró image_blob ni se pudo resolver 'latest' en el bucket.")

            local_img = os.path.join(tmp, "image.jpg")
            self.gcs.download_blob_to_path(image_blob, local_img)

            img_prob = self.img_model.predict_proba(local_img)

            # Audio opcional (placeholder defendible)
            aud_prob: Optional[float] = None
            if settings.USE_AUDIO:
                # Aquí puedes implementar un clasificador ligero si consigues dataset.
                # De momento, dejamos aud_prob=None o 0.5 por “unknown”.
                aud_prob = 0.5

            final_score = settings.IMAGE_WEIGHT * img_prob + (settings.AUDIO_WEIGHT * aud_prob if aud_prob is not None else 0.0)
            status = self._status_from_score(final_score)

            return InferenceResult(
                image_probability=img_prob,
                audio_probability=aud_prob,
                final_score=final_score,
                status=status,
                meta={"image_blob": image_blob, "audio_blob": audio_blob}
            )
