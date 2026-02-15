# GEMINI Project Context: MapleScript Automation

## Project Overview

This is a Python-based automation project for the online game *MapleStory*. Its primary purpose is to automate repetitive in-game tasks, such as completing daily quests, fighting bosses, and managing collections.

The architecture is composed of three main parts:
1.  **A Graphical User Interface (GUI)**: Built with `PySide6`, acting as the main control center for users. It provides a modern, dark-themed interface to start/stop tasks and view execution logs.
2.  **A Python control script (Backend)**: Running on a **Windows** host computer. It uses computer vision libraries (`PyAutoGUI`, `OpenCV`, `Pillow`) and Windows-specific APIs (`pywin32`) to interact with the game window. It recognizes game elements by matching them against images in the `photos/` directory to decide on the next action.
3.  **A Seeed Studio Xiao ESP32S3 microcontroller**: Acting as a hardware-level input device. It runs `CircuitPython` and receives commands from the host PC via a USB serial connection. It translates these commands into actual keyboard presses and mouse movements, making the automation difficult to distinguish from human input.

The core logic is encapsulated in `src/MapleScript.py`, which provides base functionalities and **thread-safety mechanisms**. Computer vision tasks are delegated to `src/utils/maple_vision.py`. Low-level window management is handled by `src/utils/windows_object.py`. Specific automation routines (e.g., `MapleGrind`, `DailyBoss`, `RouteRecorder`) inherit from the base `MapleScript` class.

Settings are managed by a **hybrid storage system**:
- **General Preferences & Dynamic Data**: Stored as JSON files in `AppData/Local` (managed by `SettingsManager`). This includes skill configurations, recorded routes, and task-specific toggles.
- **Sensitive Data (e.g., Passwords)**: Securely managed using Windows Credential Manager via `SecretManager`.
- **Resource Paths & Static Config**: Managed by `YamlLoader` for `config/config.yaml`.

## Building and Running

### 1. Hardware Setup

- A board with the appropriate version of CircuitPython is required (e.g., Seeed Studio Xiao ESP32S3).
- Load the code from the `code/` directory onto the Xiao board.

### 2. Software Dependencies

**Important:** This project is designed for **Windows only**.

Install the required Python packages:
```bash
pip install -r requirements.txt
```
Key dependencies include `PySide6`, `qdarkstyle`, `pywin32`, `opencv-python`, `PyAutoGUI`, `pynput`, `pyserial`, and `keyring`.

### 3. Running the Application

To launch the graphical interface:
```bash
python main.py
```
This will open the "Guai Guai Automation Control Center". You can click buttons to start tasks and use the "STOP" button to interrupt them immediately.

## Architecture & Conventions

### Directory Structure
- `main.py`: **GUI Entry Point**. Initializes the `PySide6` application and hardware connection.
- `src/`: Core logic and task implementations.
    - `MapleScript.py`: Base class for all scripts.
    - `MapleGrind.py`: Automation for hunting/grinding.
    - `RouteRecorder.py`: Tool for recording keyboard input sequences.
    - `DailyBoss.py`, `DailyPrepare.py`, `MonsterCollection.py`, `Storage.py`, `DancingMachine.py`: Specific task modules.
- `src/ui/`: Contains GUI-related code.
    - `app_window.py`: The main window layout and signal/slot logic.
    - `task_manager.py`: Manages background threads for script execution.
    - `grind_settings_dialog.py`: Specialized dialog for configuring grind skills and route recording.
- `src/utils/`: Shared utilities and helpers.
    - `xiao_controller.py`: Manages serial communication with the hardware.
    - `settings_manager.py`: Implements the hybrid storage system with path virtualization (`$APP_DATA$`).
- `code/`: CircuitPython code for the Xiao ESP32S3 hardware.
- `config/`: Static configuration files (`config.yaml`).
- `photos/`: Image templates for computer vision matching.
- `tools/`: Supplementary tools like `KeyLogger.py`.

### Threading & UI Safety
- **Event-Driven:** Scripts run in a separate worker thread (`TaskManager`), not the main UI thread.
- **Interruption:** All loops in scripts MUST check `self.should_continue()` regularly.
- **Sleep:** Use `self.sleep(seconds)` instead of `time.sleep()`. This allows the script to wake up immediately when stopped.
- **Logging:** Use `self.log("message")` instead of `print()`. This sends the message to the GUI via a thread-safe signal.

### Configuration & Storage
- **AppData Storage**: `SettingsManager` virtualizes paths and routes data into specific subdirectories in `AppData/Local/MapleScriptTeam/MapleScript`:
    - `skills/`: User-defined skill images and hotkeys.
    - `routes/`: Recorded keyboard sequences (`recorded_route.json`).
    - `tasks/`: Toggles and parameters for various automation tasks.
    - `system/`: Hardware serial numbers and connection settings.
- **Path Virtualization**: Uses the `$APP_DATA$` prefix in JSON files to ensure absolute image paths are correctly resolved across different environments.
- **Static Config**: `config/config.yaml` contains UI offsets and image paths that are constant for all users.

### Hardware Communication
- All hardware actions are routed through `src/utils/xiao_controller.py`.
- **Automatic Connection**: The controller identifies the correct COM port by matching the **Serial Number** stored in user settings.
- **Controller Mocker**: If hardware is not found, a `ControllerMocker` is used to allow the GUI to run without failing, though actions won't be sent to the game.