# GEMINI Project Context: MapleScript Automation

## Project Overview

This is a Python-based automation project for the online game *MapleStory*. Its primary purpose is to automate repetitive in-game tasks, such as completing daily quests, fighting bosses, and managing collections.

The architecture is composed of three main parts:
1.  **A Graphical User Interface (GUI)**: Built with `PySide6`, acting as the main control center for users. It provides a modern, dark-themed interface to start/stop tasks and view execution logs.
2.  **A Python control script (Backend)**: Running on a **Windows** host computer. It uses computer vision libraries (`PyAutoGUI`, `OpenCV`, `Pillow`) and Windows-specific APIs (`pywin32`) to interact with the game window. It recognizes game elements by matching them against images in the `photos/` directory to decide on the next action.
3.  **A Seeed Studio Xiao ESP32S3 microcontroller**: Acting as a hardware-level input device. It runs `CircuitPython` and receives commands from the host PC via a USB serial connection. It translates these commands into actual keyboard presses and mouse movements, making the automation difficult to distinguish from human input.

The core logic is encapsulated in `src/MapleScript.py`, which provides base functionalities and **thread-safety mechanisms**. Computer vision tasks are delegated to `src/utils/maple_vision.py`. Low-level window management is handled by `src/utils/windows_object.py`. Specific automation routines (e.g., `MapleGrind`, `DailyBoss`) inherit from the base `MapleScript` class.

Settings are separated into resource paths (`config/config.yaml`) and user preferences (`config/settings.yaml`).

## Building and Running

### 1. Hardware Setup

- A Seeed Studio Xiao ESP32S3 board is required.
- Flash the board with the appropriate version of CircuitPython.
- Load the code from the `XiaoCode/` directory onto the Xiao board.

### 2. Software Dependencies

**Important:** This project is designed for **Windows only**.

Install the required Python packages:
```bash
pip install -r requirements.txt
```
Key dependencies include `PySide6`, `qdarkstyle`, `pywin32`, `opencv-python`, and `PyAutoGUI`.

### 3. Running the Application

The project supports two modes: **GUI Mode** (recommended) and **CLI Mode** (legacy/debug).

**Option A: GUI Mode (Control Center)**
To launch the graphical interface:
```bash
python main.py
```
This will open the "Guai Guai Automation Control Center". You can click buttons to start tasks and use the "STOP" button to interrupt them immediately.

**Option B: CLI Mode**
To execute a specific automation task directly from the terminal (useful for debugging):
```bash
python -m src <task_name>
```
Available task names: `grind`, `collection`, `daily`, `daily_boss`, `storage`, `dance`.

## Architecture & Conventions

### Directory Structure
- `main.py`: **GUI Entry Point**. Initializes the `PySide6` application and hardware connection.
- `src/__main__.py`: **CLI Entry Point**.
- `src/ui/`: Contains GUI-related code.
    - `app_window.py`: The main window layout and signal/slot logic.
    - `task_manager.py`: Manages background threads for script execution.
    - `settings_manager.py`: Handles reading/writing of user preferences (`settings.yaml`).
    - `settings_dialog.py`: A generic QDialog for toggling task settings.
- `src/MapleScript.py`: **Base Class**. Now implements `threading.Event` for interrupt control (`stop()`, `should_continue()`) and a logging callback (`log()`).

### Threading & UI Safety
- **Event-Driven:** Scripts run in a separate worker thread, not the main UI thread.
- **Interruption:** All loops in scripts MUST check `self.should_continue()` regularly.
- **Sleep:** Use `self.sleep(seconds)` instead of `time.sleep()`. This allows the script to wake up immediately when stopped.
- **Logging:** Use `self.log("message")` instead of `print()`. This sends the message to the GUI via a thread-safe signal.
- **UI Updates:** Scripts must NEVER modify UI elements directly. They must use the provided `log_callback`.

### Configuration
- **Resource Configuration (`config/config.yaml`):** Stores read-only data like image paths and UI offsets.
- **User Settings (`config/settings.yaml`):** Stores user-configurable boolean flags (e.g., enabling/disabling specific daily tasks). Managed by `SettingsManager`.
- **Patrol Routes:** Defined in `config/grind_routes.yaml`.
- **Secrets:** Managed using a `.env` file (see `example_env.txt`).

### Hardware Communication
- All hardware actions are routed through `src/utils/xiao_controller.py`.
- In GUI mode, the controller connection is managed by `main.py` using a context manager (`with` statement) to ensure proper resource release.