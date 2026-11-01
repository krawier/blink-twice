# BlinkType: Hands-Free Medical Communicator

Communicate using only your eyes. BlinkType uses OpenCV and cvzone's FaceMesh module to track your eyelid in real time and lets you spell out short messages from a predefined medical dictionary (in Polish) – designed for patients who cannot speak or move, e.g. in a hospital bed.

Instead of typing every letter of the alphabet, the program only offers letters that can continue a word from the dictionary, so most words need just a few selections.

## Features
- **Auto-calibration** – measures your natural resting eye openness at startup and sets the blink threshold for you.
- **Predictive letter scanning** – only letters that lead to a valid dictionary word are offered.
- **Dwell-time selection** – keep your eyes open to confirm the current letter; no precise blink counting needed.
- **Voice feedback** – every offered letter and every action is read aloud (Polish voice if available).
- **Live eye-ratio plot** – a graph of your eye openness is shown next to the camera feed, which helps with positioning and debugging.

## Installation
1. Clone this repository and open the project in VS Code.
2. Create and activate a virtual environment:

   python -m venv .env
   .\.env\Scripts\activate   # Windows PowerShell

3. Make sure VS Code uses the `.env` interpreter (Command Palette → *Python: Select Interpreter*).
4. Install dependencies:

   pip install -r requirements.txt

   (Main packages: `opencv-python`, `cvzone`, `mediapipe`, `pyttsx3`, `numpy`.)

5. *(Optional)* Install a Polish text-to-speech voice in your operating system (e.g. "Paulina" on Windows). Without it, the default system voice is used.

## Running

   python blink_counter.py

Press `q` to quit.

The window shows three panels: **camera feed**, **control panel** (state, current prefix, offered letter, dwell progress bar, number of matching words) and **live eye-ratio graph**.

## How to use

Times below assume a camera running at about 30 FPS – the program counts frames, so on a slower camera every action takes proportionally longer.

### 1. Calibration
After launch, the panel shows **STARE AT CAMERA**. Look at the camera normally with your eyes open (blinking naturally is fine) for about **12 seconds**, until the message disappears and the state shows **IDLE**.

### 2. Controls

| Action | How | When |
|---|---|---|
| **Start typing** | Close your eyes for **~2.5 s**, then open them | In `IDLE` |
| **Next letter** | Short, deliberate blink (**~0.1–1 s**) | In `SCANNING` |
| **Select letter** | Keep your eyes **open for ~2 s** – the green bar fills up | In `SCANNING` |
| **Cancel message** | Close your eyes for **~2 s**, then open them | In `SCANNING` |

Blinks lasting between ~1 s and ~2 s in `SCANNING` mode are ignored – this protects against accidental actions.

### 3. Typing a word – step by step
1. Enter `SCANNING` mode. The program speaks the first available letter.
2. Blink briefly to move to the next letter. Each letter is spoken aloud; the panel also shows which letter comes next. The list wraps around after the last letter.
3. When you hear the letter you want, simply **keep your eyes open**. After ~2 s the program says **"Wybrano"** and adds the letter to the prefix.
4. The list of letters shrinks to those that continue a matching word. When only one word remains, just wait – each remaining letter is selected automatically after ~2 s.
5. If the letters typed so far already form a complete word, but longer words also match (e.g. **NIE** / **NIEWYGODNIE**), a **WYSLIJ** option appears first – wait to send the shorter word, or blink to continue typing the longer one.
6. When the message is complete, the program says **"Wysłano komunikat"** and returns to `IDLE`. The message is currently printed to the console as `--- SENT TO DASHBOARD: <WORD> ---`.

**Example – "WODA":** start typing → blink until you hear *W* → wait → the remaining letters *O*, *D*, *A* are the only options, so just keep waiting → message sent.

**Example – "NIE":** start typing → blink until you hear *N* → wait → *I* and *E* are selected automatically → **WYSLIJ** is offered → wait → message sent.

### 4. Available words
| Category | Words |
|---|---|
| Urgent | BÓL, DUSZNO, PANIKA, POMOC, SSAK, PIELĘGNIARKA, LEKARZ, LEKI, KROPLÓWKA |
| Physiological needs | WODA, JEDZENIE, TOALETA, MOKRO, ZIMNO, GORĄCO |
| Comfort | PODUSZKA, KOC, SIEDZIEĆ, LEŻEĆ, OBRÓCIĆ, NIEWYGODNIE, SWĘDZI, SKURCZ |
| Environment | ŚWIATŁO, CICHY, GŁOŚNO, ZAMKNIJ, OTWÓRZ |
| Communication / personal | TAK, NIE, DZIĘKUJĘ, TELEFON, OKULARY, RODZINA |

The dictionary can be edited in the `medical_dictionary` list in the source code. Words that are the beginning of other words are handled automatically with the **WYSLIJ** option.

## Best practices for camera tracking
- **Distance:** sit slightly further from the camera so your whole head, including chin and jawline, is visible – FaceMesh needs it to anchor the mesh.
- **Angle:** face the camera with a slight tilt so your eyelids are clearly visible. Only one eye is measured, so keep it unobstructed (no hair, glasses glare).
- **Lighting:** light your face evenly from the front; shadows over the eyes cause false blinks.
- **Recalibrate** (restart the program) if you change position, distance or lighting significantly.

## Known limitations
- Polish characters (Ą, Ę, Ó, Ł, Ś…) are not rendered correctly by OpenCV and appear as `?` on screen; voice feedback is not affected.
- All timings depend on the camera's frame rate.
- Messages are only printed to the console; sending them to an external dashboard is not implemented yet.