# Face Attendance Recognition with Python

This project builds a face attendance system inspired by the linked Computer Vision Engineer tutorial flow:

- register a person from the webcam
- generate face encodings
- open a live recognition window
- save attendance into SQLite and CSV
- review attendance in a desktop dashboard

## Features

- webcam-based face registration
- face encoding rebuild from saved images
- real-time recognition with OpenCV
- SQLite-backed attendance records
- daily CSV export for compatibility
- Tkinter desktop GUI dashboard
- CLI commands for Windows or any Python environment

## Project Structure

```text
cv/
|-- data/
|   |-- faces/
|   |-- logs/
|   |-- attendance.db
|-- face_attendance/
|   |-- __init__.py
|   |-- attendance.py
|   |-- config.py
|   |-- database.py
|   |-- gui.py
|   |-- registration.py
|   |-- storage.py
|-- main.py
|-- requirements.txt
```

## Setup

1. Create a virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

Notes:

- Use Python 3.10 or 3.11 on Windows. Python 3.12+ usually fails because `face-recognition` depends on `dlib`.
- On this machine, Python 3.13.3 is installed, so create a 3.11 environment first before installing requirements.

## Usage

Register a person from the webcam:

```powershell
python main.py register --name Bijal --samples 5
```

Rebuild encodings from the saved face images:

```powershell
python main.py rebuild
```

Start live attendance:

```powershell
python main.py attendance
```

Launch the GUI dashboard:

```powershell
python main.py gui
```

Attendance is saved to:

```text
data/logs/attendance_YYYY-MM-DD.csv
```

Database is saved to:

```text
data/attendance.db
```

## Controls

- During registration, press `q` to cancel.
- During attendance, press `q` to quit the webcam window.

## Tips

- Register faces in good lighting.
- Keep only one face visible while registering.
- Re-register someone if recognition is weak.
