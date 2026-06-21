# GEMINI Project Context: MapleScript Automation

## Project Overview

This is a Python-based automation project for the online game *MapleStory*. Its primary purpose is to automate repetitive in-game tasks, such as completing daily quests, fighting bosses, and managing collections.

The architecture is composed of three main parts:
1.  **A Graphical User Interface (GUI)**: Built with `PySide6`, acting as the main control center for users. It provides a modern, dark-themed interface to start/stop tasks and view execution logs.
2.  **A Python control script (Backend)**: Running on a **Windows** host computer. It uses computer vision libraries (`mss`, `OpenCV`, `Pillow`) and Windows-specific APIs (`pywin32`) to interact with the game window. It recognizes game elements by matching them against images in the `photos/` directory to decide on the next action. AI-powered rune detection is handled by `src/utils/rune_detector.py` using TFLite models in `models/`.
3.  **A Seeed Studio Xiao ESP32S3 microcontroller**: Acting as a hardware-level input device. It runs `CircuitPython` and receives commands from the host PC via a USB serial connection. It translates these commands into actual keyboard presses and mouse movements, making the automation difficult to distinguish from human input.

The core logic is encapsulated in `src/MapleScript.py`, which provides base functionalities, **thread-safety mechanisms**, and **minimap-based navigation** (`move_to_point`). Computer vision tasks are delegated to `src/utils/maple_vision.py`. Low-level window management is handled by `src/utils/windows_object.py`. Specific automation routines (e.g., `MapleGrind`, `DailyBoss`, `RouteRecorder`) inherit from the base `MapleScript` class. Particularly, the grinding automation ([MapleGrind](src/MapleGrind.py)) is implemented using a Finite State Machine (FSM) architecture, delegating state behaviors to individual classes under `src/states/` and managed by [MapleMachine.py](src/MapleMachine.py).

Settings and resources are managed by a **hybrid storage system**:
- **General Preferences & Dynamic Data**: Stored as JSON files in `AppData/Local` (managed by `SettingsManager`). This includes skill configurations, recorded routes, and task-specific toggles.
- **Sensitive Data (e.g., Passwords)**: Securely managed using Windows Credential Manager via `SecretManager`.
- **Resource Management & Static Config**: Managed by `YamlLoader` in `src/utils/config_loader.py`. It loads static configurations from `config/config.yaml` and **caches image resources** as `PIL.Image` objects for global use.

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
Key dependencies include `PySide6`, `qdarkstyle`, `pywin32`, `opencv-python`, `mss`, `Pillow`, `pynput`, `pyserial`, `keyring`, `pyyaml`, and `ai-edge-litert`.

### 3. Running the Application

To launch the graphical interface:
```bash
python main.py
```
This will open the "Guai Guai Automation Control Center". You can click buttons to start tasks and use the "STOP" button to interrupt them immediately.

### 4. CI/CD & Automated Packaging

The project uses GitHub Actions for automated build and release workflows. The workflow is defined in [.github/workflows/python-app.yml](.github/workflows/python-app.yml):
- **Package Management**: Uses `uv` (`setup-uv`) as the package and environment manager to accelerate the installation and caching of dependency packages (`requirements.txt`).
- **Compilation & Bundling**: Uses `Nuitka` via `uv run python -m nuitka` to compile the standalone executable, excluding unnecessary PySide6 modules to compress the output size, and publishes the bundled `main.zip` to GitHub Releases.

## Architecture & Conventions

### Directory Structure
- `main.py`: **GUI Entry Point**. Initializes the `PySide6` application and hardware connection.
- `.github/workflows/python-app.yml`: GitHub Actions workflow configuration file, utilizing `uv` and `Nuitka` for automated compilation and release of the Windows standalone executable.
- `src/`: Core logic and task implementations.
    - `MapleScript.py`: Base class for all scripts. Includes minimap navigation (`move_to_point`), input handling, and hardware safety mechanisms.
    - `MapleGrind.py`: Entry point for hunting/grinding automation. It initializes the state machine to run the grind loop.
    - `MapleMachine.py`: State machine manager (`Machine`) that drives the grinding loop, handles state transitions, and manages an interruption stack.
    - `states/`: Directory containing concrete states for the grinding FSM (detailed documentation in [src/states/README.md](src/states/README.md)):
        - `base.py`: The abstract base class for all states.
        - `stationary.py`, `walker.py`, `wander.py`: Core behaviors (grinding, loop route, random wander).
        - `runesolver.py`, `pause.py`: Interruption states for solving runes and pausing when unsafe.
        - `waiting.py`: Idle states used during cooldown periods.
    - `RouteRecorder.py`: Tool for recording keyboard input sequences.
    - `DailyBoss.py`, `DailyPrepare.py`, `MonsterCollection.py`, `Storage.py`, `DancingMachine.py`: Specific task modules.
- `src/ui/`: Contains GUI-related code.
    - `app_window.py`: The main window layout and signal/slot logic.
    - `task_manager.py`: Manages background threads for script execution.
    - `grind_settings_dialog.py`: Specialized dialog for configuring grind skills and route recording.
    - `settings_dialog.py`, `hardware_setup_dialog.py`, `storage_settings_dialog.py`: Dialogs for system and task configuration.
- `src/utils/`: Shared utilities and helpers.
    - `xiao_controller.py`: Manages serial communication with the hardware.
    - `settings_manager.py`: Implements the hybrid storage system with path virtualization (`$APP_DATA$`).
    - `config_loader.py`: (`YamlLoader`) Loads static configurations from `config.yaml` and manages image resources.
    - `rune_detector.py`: AI-based rune arrow detection using TFLite.
    - `windows_object.py`: Window handle and state management.
    - `maple_vision.py`: Computer vision and minimap analysis.
- `code/`: CircuitPython code for the Xiao ESP32S3 hardware.
- `config/`: Static configuration files (`config.yaml`).
- `models/`: TFLite models and labels for AI tasks (e.g., `model_unquant.tflite`).
- `photos/`: Image templates for computer vision matching.
- `tools/`: Supplementary tools like `KeyLogger.py`.

### Coordinate Systems & Multi-Monitor Support
- **Primary-Monitor Relative**: The project uses the standard Windows coordinate system where the **top-left of the primary monitor is (0,0)**.
- **Unified Logic**: Both `mss` (for screen capture) and `win32api` (for mouse/window positioning) operate in this same virtual screen coordinate space. 
- **No Manual Offsets for Capture**: Do not apply manual offsets like `screen_offset` or virtual screen normalization for full-screen or window-level capture.
- **UI Offsets for Detection**: Specific interaction areas (e.g., skill slots, minimap, rune arrows) are defined using `ui_offsets` in `config.yaml` relative to the game window's client area.

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
- **Static Config & Resource Manager**: `YamlLoader` (`config_loader.py`) centralizes UI offsets and image resources, providing pre-loaded `PIL.Image` objects to scripts.

### Grinding State Machine (FSM)
The grinding routine ([MapleGrind](src/MapleGrind.py)) is structured as a Finite State Machine managed by `Machine` ([MapleMachine.py](src/MapleMachine.py)) to decouple behavior logic (see [src/states/README.md](src/states/README.md) for detailed architecture):
- **State Transition by Keys**: To prevent circular imports, states return string keys (e.g., `"WALKER"`, `"RUNESOLVER"`) during status checks. The machine maps these to concrete state classes via `state_mapping`.
- **Stack-based Interruption**: When an unsafe condition occurs or a rune appears, the active state is pushed onto a stack (`Machine.stack`) and replaced by `Pause` or `RuneSolver`. Once resolved, the state is popped back to resume where it left off.
- **Cooldown & Wait Variants**: States like `Walker` and `Wander` support cooldown intervals, split into active grinding cooldown (`WalkerCoolDown`) and idle waiting (`WalkerWaiting`) based on user configurations.

### Hardware Communication
- All hardware actions are routed through `src/utils/xiao_controller.py`.
- **Automatic Connection**: The controller identifies the correct COM port by matching the **Serial Number** stored in user settings.
- **Safety Mechanism**: Scripts must use `release_all()` in `finally` blocks or upon interruption to ensure no keys remain pressed on the hardware level.
- **Controller Mocker**: If hardware is not found, a `ControllerMocker` is used to allow the GUI to run without failing, though actions won't be sent to the game.