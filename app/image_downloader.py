from pathlib import Path
from typing import Optional

from app.gcs_client import GCSClient, GCSConfig
from app.settings import settings


class ImageDownloader:
    """
    Descarga imágenes desde Google Cloud Storage
    y las guarda localmente de forma persistente.
    """

    def __init__(self, output_dir: str = "downloaded_images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.gcs = GCSClient(
            GCSConfig(
                sa_json_path=settings.GCS_SA_JSON,
                bucket_name=settings.GCS_BUCKET,
            )
        )

    def download(self, image_blob: str) -> Path:
        """
        Descarga un blob de imagen desde GCS y lo guarda localmente.
        Retorna la ruta local del archivo.
        """
        filename = Path(image_blob).name
        local_path = self.output_dir / filename

        self.gcs.download_blob_to_path(
            blob_name=image_blob,
            out_path=str(local_path),
        )

        return local_path
