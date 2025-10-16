# GEMINI Project Context: MapleScript Automation

## Project Overview

This is a Python-based automation project for the online game *MapleStory*. Its primary purpose is to automate repetitive in-game tasks, such as completing daily quests, fighting bosses, and managing collections.

The architecture is composed of two main parts:
1.  **A Python control script** running on the host computer. It uses computer vision libraries (`PyAutoGUI`, `OpenCV`, `Pillow`) to capture the screen, recognize game elements by matching them against images in the `photos/` directory, and decide on the next action.
2.  **A Seeed Studio Xiao ESP32S3 microcontroller** acting as a hardware-level input device. It runs `CircuitPython` and receives commands from the host PC via a USB serial connection. It then translates these commands into actual keyboard presses and mouse movements, making the automation difficult to distinguish from human input.

The core logic seems to be encapsulated in `MapleScript.py`, with specific automation routines implemented in other files like `DailyBoss.py`, `MonsterCollection.py`, etc.

## Building and Running

### 1. Hardware Setup

- A Seeed Studio Xiao ESP32S3 board is required.
- Flash the board with the appropriate version of CircuitPython.
- Load the code from the `XiaoCode/` directory onto the Xiao board. The board must be configured to act as a HID (keyboard/mouse) device.

### 2. Software Dependencies

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

- **Class-based Structure:** The project appears to use an object-oriented approach, with a base `MapleScript` class defining common functionalities and task-specific classes inheriting from it.
- **Image-driven Logic:** The core of the automation logic relies on image recognition. To add new features, you must:
    1.  Add new template images (screenshots of UI elements, characters, etc.) to the `photos/` directory.
    2.  Write Python code to locate these images on screen and trigger corresponding actions via the `XiaoController.py`.
- **Hardware Communication:** All hardware-level keyboard and mouse actions are routed through `XiaoController.py`, which communicates with the Xiao microcontroller. Direct calls to `pydirectinput` or `PyAutoGUI` for control should probably be avoided in favor of using the controller.
- **Configuration:** There are no obvious configuration files. Settings like timings, coordinates, or specific logic are likely hardcoded within the Python scripts themselves.
