from __future__ import annotations

import pickle
from pathlib import Path

import face_recognition

from .config import ENCODINGS_PATH, FACES_DIR, ensure_directories


def _iter_image_files(directory: Path) -> list[Path]:
    patterns = ("*.jpg", "*.jpeg", "*.png")
    image_files: list[Path] = []
    for pattern in patterns:
        image_files.extend(directory.glob(pattern))
    return sorted(image_files)


def rebuild_encodings(faces_dir: str | None = None) -> int:
    ensure_directories()
    source_dir = Path(faces_dir) if faces_dir else FACES_DIR

    known_names: list[str] = []
    known_encodings: list[list[float]] = []

    if not source_dir.exists():
        raise FileNotFoundError(f"Faces directory not found: {source_dir}")

    for person_dir in sorted(p for p in source_dir.iterdir() if p.is_dir()):
        for image_path in _iter_image_files(person_dir):
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if not encodings:
                print(f"Skipping {image_path.name}: no face found.")
                continue

            known_names.append(person_dir.name)
            known_encodings.append(encodings[0].tolist())

    with ENCODINGS_PATH.open("wb") as handle:
        pickle.dump({"names": known_names, "encodings": known_encodings}, handle)

    return len(known_names)


def load_encodings() -> tuple[list[str], list]:
    ensure_directories()
    if not ENCODINGS_PATH.exists():
        raise FileNotFoundError(
            "No encodings found. Register faces first or run `python main.py rebuild`."
        )

    with ENCODINGS_PATH.open("rb") as handle:
        payload = pickle.load(handle)

    return payload["names"], payload["encodings"]
