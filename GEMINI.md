# GEMINI Project Context: MapleScript Automation

## Project Overview

This is a Python-based automation project for the online game *MapleStory*. Its primary purpose is to automate repetitive in-game tasks, such as completing daily quests, fighting bosses, and managing collections.

The architecture is composed of two main parts:
1.  **A Python control script** running on a **Windows** host computer. It uses computer vision libraries (`PyAutoGUI`, `OpenCV`, `Pillow`) and Windows-specific APIs (`pywin32`) to interact with the game window. It recognizes game elements by matching them against images in the `photos/` directory to decide on the next action.
2.  **A Seeed Studio Xiao ESP32S3 microcontroller** acting as a hardware-level input device. It runs `CircuitPython` and receives commands from the host PC via a USB serial connection. It then translates these commands into actual keyboard presses and mouse movements, making the automation difficult to distinguish from human input.

The core logic is encapsulated in `src/MapleScript.py`, which provides base functionalities. Computer vision tasks, such as minimap analysis and player detection, are delegated to `src/utils/maple_vision.py`. Low-level window management and screen coordinate calculations are handled by `src/utils/windows_object.py`. Specific automation routines, like `src/DailyPrepare.py`, `src/MonsterCollection.py`, `src/MapleGrind.py`, `src/DailyBoss.py`, `src/Storage.py`, and `src/DancingMachine.py`, inherit from the base `MapleScript` class.

The project is now **configuration-driven**, with skills, UI elements, and settings defined in `config/config.yaml` and loaded by the `YamlLoader` class in `src/utils/config_loader.py`. The grinding script (`src/MapleGrind.py`) uses minimap analysis to determine the character's position and execute patrol routes defined in `config/grind_routes.yaml`.

All tasks are executed through the main entry point `src/__main__.py`.

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

To execute a specific automation task, run `src/__main__.py` with the desired task as an argument.

- To run the daily preparation routine:
  ```bash
  python -m src daily
  ```
- To run the monster collection routine:
  ```bash
  python -m src collection
  ```
- To run the grinding routine:
  ```bash
  python -m src grind
  ```
- To run the daily boss routine:
  ```bash
  python -m src daily_boss
  ```
- To run the storage input routine:
  ```bash
  python -m src storage
  ```
- To run the dancing machine routine:
  ```bash
  python -m src dance
  ```

### 4. Testing

There is no dedicated testing framework (like `pytest` or `unittest`) apparent in the project. Testing is likely performed by running the scripts directly and visually verifying their behavior in the game.

## Development Conventions

- **Class-based Structure:** The project uses an object-oriented approach, with a base `MapleScript` class defining common functionalities and task-specific classes inheriting from it.

- **Configuration-driven Logic:** Most of the dynamic settings are managed in `config/config.yaml`. This is the single source of truth for parameters that might change, making the scripts more flexible and easier to maintain. This includes:
    - **Skills:** Defining skill names, their assigned keys, and the corresponding image files for cooldown detection.
    - **Script Parameters:** Adjusting values like the time gap between skill casts for the grinding script.
    - **Bosses and UI Elements:** Defining image paths for daily bosses, storage UI numbers, and various UI elements for daily routines.
    - **Activity Settings:** Specific configurations for activities like the Dancing Machine (directions, UI elements) and Monster Collection.
    - **Example:** To add a new skill, you only need to add an entry to `config/config.yaml` under the `skills` section and place the corresponding cooldown image in the `photos/` directory. No code changes are required.

- **Secrets Management (.env)**: Sensitive information, such as the second password for the storage, is managed using a `.env` file in the project root.
    - This file is **not** committed to version control and should be listed in `.gitignore`.
    - The base `MapleScript` class automatically loads variables from this file using `python-dotenv`.
    - A template file, `.env.example`, should be maintained to show required environment variables.

- **Hardware Communication:** All hardware-level keyboard and mouse actions are routed through `src/utils/xiao_controller.py`, which communicates with the Xiao microcontroller.

- **Keystroke Recording:** The project includes a `tools/KeyLogger.py` utility. This tool can be run to record a sequence of keystrokes and their timings, which is useful for creating complex, hardcoded movement or action sequences like the patrol routes found in `config/grind_routes.yaml`.