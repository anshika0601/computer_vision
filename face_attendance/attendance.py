from __future__ import annotations

from datetime import datetime

import cv2
import face_recognition

from .config import LOGS_DIR, ensure_directories
from .database import has_attendance_for_date, init_database, mark_attendance
from .storage import load_encodings


def _today_log_path():
    ensure_directories()
    return LOGS_DIR / f"attendance_{datetime.now().date().isoformat()}.csv"


def _append_attendance_csv(log_path, name: str, attendance_date: str, attendance_time: str) -> None:
    import csv

    file_exists = log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not file_exists:
            writer.writerow(["name", "date", "time", "status"])
        writer.writerow([name, attendance_date, attendance_time, "Present"])


def run_attendance(camera_index: int = 0, tolerance: float = 0.5) -> None:
    ensure_directories()
    init_database()
    known_names, known_encodings = load_encodings()
    if not known_encodings:
        raise RuntimeError("No face encodings available. Register someone first.")

    log_path = _today_log_path()
    today = datetime.now().date().isoformat()
    marked_names = {name for name in known_names if has_attendance_for_date(name, today)}

    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise RuntimeError(f"Unable to open webcam at index {camera_index}.")

    process_this_frame = True

    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Failed to read a frame from the webcam.")

            face_locations = []
            face_names = []

            if process_this_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_encodings,
                        face_encoding,
                        tolerance=tolerance,
                    )
                    name = "Unknown"

                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    if len(face_distances) > 0:
                        best_match_index = face_distances.argmin()
                        if matches[best_match_index]:
                            name = known_names[best_match_index]

                    if name != "Unknown" and name not in marked_names:
                        attendance_date, attendance_time = mark_attendance(name)
                        _append_attendance_csv(log_path, name, attendance_date, attendance_time)
                        marked_names.add(name)
                        print(f"Attendance marked for {name}.")

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(
                    frame,
                    name,
                    (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.8,
                    (255, 255, 255),
                    1,
                )

            cv2.putText(
                frame,
                "Press 'q' to quit attendance",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2,
            )
            cv2.imshow("Face Attendance", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
