from __future__ import annotations

from datetime import datetime

import cv2
import face_recognition

from .config import FACES_DIR, ensure_directories
from .database import init_database, upsert_person
from .storage import rebuild_encodings


def capture_face_samples(name: str, samples: int = 5, camera_index: int = 0) -> None:
    ensure_directories()
    init_database()
    normalized_name = name.strip().replace(" ", "_")
    person_dir = FACES_DIR / normalized_name
    person_dir.mkdir(parents=True, exist_ok=True)
    upsert_person(normalized_name)

    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise RuntimeError(f"Unable to open webcam at index {camera_index}.")

    saved_count = 0

    try:
        while saved_count < samples:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Failed to read a frame from the webcam.")

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            message = f"Registering {normalized_name}: {saved_count}/{samples}"
            helper = "Show one clear face and press 's' to save, 'q' to quit."
            cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, helper, (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

            for top, right, bottom, left in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

            cv2.imshow("Face Registration", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("Registration cancelled.")
                return

            if key == ord("s"):
                if len(face_locations) != 1:
                    print("Please keep exactly one face in frame before saving.")
                    continue

                file_name = datetime.now().strftime("%Y%m%d_%H%M%S_%f.jpg")
                output_path = person_dir / file_name
                cv2.imwrite(str(output_path), frame)
                saved_count += 1
                print(f"Saved sample {saved_count}/{samples}: {output_path.name}")

        total = rebuild_encodings()
        print(f"Registration complete. Encodings rebuilt with {total} sample(s).")
    finally:
        camera.release()
        cv2.destroyAllWindows()
