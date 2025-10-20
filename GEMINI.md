# GEMINI Project Context: MapleScript Automation

## Project Overview

This is a Python-based automation project for the online game *MapleStory*. Its primary purpose is to automate repetitive in-game tasks, such as completing daily quests, fighting bosses, and managing collections.

The architecture is composed of two main parts:
1.  **A Python control script** running on a **Windows** host computer. It uses computer vision libraries (`PyAutoGUI`, `OpenCV`, `Pillow`) and Windows-specific APIs (`pywin32`) to interact with the game window. It recognizes game elements by matching them against images in the `photos/` directory to decide on the next action.
2.  **A Seeed Studio Xiao ESP32S3 microcontroller** acting as a hardware-level input device. It runs `CircuitPython` and receives commands from the host PC via a USB serial connection. It then translates these commands into actual keyboard presses and mouse movements, making the automation difficult to distinguish from human input.

The core logic is encapsulated in `MapleScript.py`, which provides base functionalities. Specific automation routines, like `DailyBoss.py`, `MonsterCollection.py`, and the new `MapleGrind.py`, inherit from this base class. The project is now configuration-driven, with skills and settings defined in `config.yaml` and loaded by `ConfigLoader.py`. The grinding script (`MapleGrind.py`) uses minimap analysis to determine the character's position and execute patrol routes.

## Building and Running

### 1. Hardware Setup

- A Seeed Studio Xiao ESP32S3 board is required.
- Flash the board with the appropriate version of CircuitPython.
- Load the code from the `XiaoCode/` directory onto the Xiao board. The board must be configured to act as a HID (keyboard/mouse) device.

### 2. Software Dependencies

**Important:** This project is designed for **Windows only** due to its reliance on the `pywin32` library for window management.

Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Running the Scripts

To execute a specific automation task, run its corresponding Python file. For example:

- To run the daily boss routine:
  ```bash
  python DailyBoss.py
  ```
- To run the monster collection routine:
  ```bash
  python MonsterCollection.py
  ```
- To run the grinding routine:
  ```bash
  python MapleGrind.py
  ```

### 4. Testing

There is no dedicated testing framework (like `pytest` or `unittest`) apparent in the project. Testing is likely performed by running the scripts directly and visually verifying their behavior in the game.

## Development Conventions

- **Class-based Structure:** The project uses an object-oriented approach, with a base `MapleScript` class defining common functionalities and task-specific classes inheriting from it.
- **Configuration-driven Logic:** Most of the dynamic settings are managed in `config.yaml`. This includes:
    - **Skills:** Defining skill names, their assigned keys, and the corresponding image files for cooldown detection.
    - **Script Parameters:** Adjusting values like the time gap between skill casts for the grinding script.
    To add or modify a skill, you only need to edit the `config.yaml` file and place the corresponding image in the `photos/` directory.
- **Hardware Communication:** All hardware-level keyboard and mouse actions are routed through `XiaoController.py`, which communicates with the Xiao microcontroller.
- **Keystroke Recording:** The project includes a `KeyLogger.py` utility. This tool can be run to record a sequence of keystrokes and their timings, which is useful for creating complex, hardcoded movement or action sequences like the patrol routes found in `MapleGrind.py`.