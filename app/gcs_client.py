from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from google.cloud import storage
from google.oauth2 import service_account


@dataclass(frozen=True)
class GCSConfig:
    sa_json_path: str
    bucket_name: str


class GCSClient:
    def __init__(self, cfg: GCSConfig) -> None:
        sa_path = Path(cfg.sa_json_path)
        if not sa_path.exists():
            raise FileNotFoundError(
                f"Service account JSON no encontrado: {sa_path}. "
                "Configura GCS_SA_JSON correctamente."
            )

        creds = service_account.Credentials.from_service_account_file(str(sa_path))
        self._client = storage.Client(credentials=creds, project=creds.project_id)
        self._bucket = self._client.bucket(cfg.bucket_name)

    def download_blob_to_path(self, blob_name: str, out_path: str) -> str:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        blob = self._bucket.blob(blob_name)
        if not blob.exists():
            raise FileNotFoundError(f"Blob no existe en bucket: {blob_name}")

        blob.download_to_filename(str(out))
        return str(out)

    def find_latest_blob(self, prefix: str):
        blobs = list(self._client.list_blobs(self._bucket, prefix=prefix))

        print("DEBUG - blobs encontrados:")
        for b in blobs:
            print(" -", b.name)

        if not blobs:
            return None

        blobs.sort(key=lambda b: b.updated or 0, reverse=True)
        return blobs[0].name

