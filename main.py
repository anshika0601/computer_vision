from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Face attendance recognition project with registration and live attendance."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser("register", help="Register a person from the webcam.")
    register_parser.add_argument("--name", required=True, help="Person name to register.")
    register_parser.add_argument(
        "--samples",
        type=int,
        default=5,
        help="Number of valid face samples to capture.",
    )
    register_parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Webcam index to use.",
    )

    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help="Rebuild face encodings from images stored in data/faces.",
    )
    rebuild_parser.add_argument(
        "--faces-dir",
        default=None,
        help="Optional custom face image directory.",
    )

    attendance_parser = subparsers.add_parser(
        "attendance",
        help="Run live face recognition and log attendance.",
    )
    attendance_parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Webcam index to use.",
    )
    attendance_parser.add_argument(
        "--tolerance",
        type=float,
        default=0.5,
        help="Face match tolerance. Lower is stricter.",
    )

    subparsers.add_parser("gui", help="Launch the desktop GUI dashboard.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if sys.version_info >= (3, 12):
        raise SystemExit(
            "Use Python 3.10 or 3.11 for this project. "
            "The `face-recognition` and `dlib` packages are typically not available "
            "for Python 3.12+ on Windows."
        )

    if args.command == "register":
        from face_attendance.registration import capture_face_samples

        capture_face_samples(name=args.name, samples=args.samples, camera_index=args.camera_index)
    elif args.command == "rebuild":
        from face_attendance.storage import rebuild_encodings

        count = rebuild_encodings(faces_dir=args.faces_dir)
        print(f"Saved {count} face encoding(s).")
    elif args.command == "attendance":
        from face_attendance.attendance import run_attendance

        run_attendance(camera_index=args.camera_index, tolerance=args.tolerance)
    elif args.command == "gui":
        from face_attendance.gui import launch_gui

        launch_gui()


if __name__ == "__main__":
    main()
