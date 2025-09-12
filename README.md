Pose Angle Viewer (MediaPipe)

Range-of-Motion (ROM) measurement and live coaching feedback from webcam or video.
Select common joints (knee, hip, trunk, ankle, shoulder), see clean on-screen angle arcs with degree labels, and export an annotated MP4 for analysis.

Why? Quick, visual ROM checks with consistent angle readouts—ideal for squat/jump coaching, rehab, and movement education.

✨ Features

Real-time pose & angles from webcam or video

Track up to 5 angles simultaneously, color-coded

Readable overlays: arcs, labels, helper markers

Save annotated MP4 (what you see is what you export)

ROM-oriented presets (knee flex/extend, hip flex/abduct, trunk/tibia inclination, shoulder tilt)

Works offline; no server required

Friendly foundation for squat and jump analysis modules

🚀 Quick Start
Requirements

Python 3.9+

Tested on Windows/macOS (wxPython required)

Installation
pip install -U opencv-python mediapipe==0.10.* wxPython numpy


If wxPython fails via pip, visit the wxPython downloads page and install the wheel for your OS/Python version.

Run
python DropBoxAngles.py

🖥️ Using the App

Open video: File → Browse Video

Live camera: File → Live Camera

Pick angles: Use the five dropdown slots (left sidebar)

Save: Click Start Save to export an annotated MP4

Tip: Use different colors per slot to visually separate joints.

📥 Inputs / 📤 Outputs

Inputs

Webcam (default camera)

Video files supported by OpenCV (e.g., MP4, AVI, MOV)

On-screen Output

Angle arcs with degree labels

Helper markers and baselines for clarity

Saved Output

Annotated MP4 with overlays baked in

📸 Demo (add your images)

Create a docs/ folder and include screenshots/GIFs. Update paths below:

Main UI
![Main UI](docs/ui-main.png)

Angle overlay (single joint)
![Angle Overlay](docs/angle-overlay.png)

Multiple angles (five slots)
![Multi Angles](docs/angles-multi.png)

Saving dialog
![Saving](docs/save-progress.png)

🧩 Angle Presets (Examples)

Knee: flexion/extension (L/R)

Hip: flexion/extension (horizontal/vertical views), abduction/adduction (L/R)

Trunk: inclination (L/R)

Tibia: inclination (L/R)

Shoulder/Head: tilt/level checks

Presets are designed for practical ROM snapshots and technique feedback.

🗂️ Project Structure
DropBoxAngles.py      # App entry point (UI & run)
mediapipe_lib.py      # Pose utilities, angle presets, drawing helpers
docs/                 # Screenshots/GIFs for README (add yours)

🔒 Privacy

Runs locally on your machine.

No frames or metrics are uploaded.

🧭 Roadmap

Movement templates (squat/jump)

Rep counting & phase markers

CSV export of angle traces

Side-by-side comparisons

Basic coaching cues (angle thresholds)

Suggestions welcome—open an issue to discuss!

❓ FAQ

Does it work without internet?
Yes. Everything runs locally.

Is it single-person pose?
Yes—optimized for one subject in frame.

Can I change colors?
Yes—each angle slot can use a different color.

🙌 Acknowledgements

Built with MediaPipe Pose, OpenCV, wxPython, and NumPy.
