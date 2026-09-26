# BlinkType: OpenCV Hands-Free Keyboard
## Translate your blinks into text using your webcam. This project uses OpenCV and cvzone's FaceMesh module to track facial geometry in real-time, auto-calibrate to your resting eye state, and convert rapid blink sequences into alphabetical characters.

# Features
- Auto-Calibration: Dynamically adjusts to your natural eye shape and distance during the first 3 seconds of runtime.
- Live Data Plotting: Visualizes your eye-aspect ratio (EAR) on a live graph alongside your camera feed.
- State-Based Deletion: Erases current progress by holding your eyes closed, using color-coded UI feedback to confirm deletion.

# Installation
- Clone this repository and open the project in VS Code.
- Create and activate a Python virtual environment:

`python -m venv .env `
`.\.env\Scripts\activate  # Windows PowerShell`

- Ensure VS Code is using your .env interpreter (Command Palette -> Python: Select Interpreter).

- Install the required dependencies using your requirements file:

`pip install -r requirements.txt`

# Usage & Typing Guide
Run the script to start the camera interface:

`python blink_counter.py`

# The Controls:
- Calibrate: When the script starts, stare at the camera normally until the "STARE AT CAMERA" text disappears.

- Spacebar (1 Blink): A single quick blink adds a space.

- Letters (2+ Blinks): Blink rapidly in sequence to select a letter, then hold your eyes open for 1 second to lock it in. (e.g., 2 blinks = A, 3 blinks = B, 21 blinks = T).

- Delete Word (Hold Closed): Close your eyes and hold them shut for about 1.5 seconds. The UI will flash Red when the word is successfully cleared.

# Best Practices for Camera Tracking
- For the FaceMesh algorithm to accurately calculate your eye ratio without hallucinating blinks, camera positioning is critical:

- Distance: The script works best when you sit slightly further away from the camera. The detector needs to see your entire head (including your chin and jawline) to anchor the 3D tracking mesh properly.

- Angle: Maintain a slight tilt towards the camera. This gives the detector a clear, unobstructed view of your eyelids and prevents your resting eye ratio from wildly fluctuating.

- Lighting: Ensure your face is well-lit from the front to avoid harsh shadows over your eyes that might confuse the contrast detection.