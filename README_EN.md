<h1 align="center">MapleScript</h1>

<p align="center">
  <img src="https://img.shields.io/github/v/release/abc21086999/maple_script" alt="Release" />
  <img src="https://img.shields.io/badge/Python-3.13-blue" alt="Python" />
  <img src="https://img.shields.io/github/downloads/abc21086999/maple_script/total?color=blue" alt="Downloads" />
</p>

<p align="center">
  <a href="README_EN.md">English</a> | <a href="README.md">繁體中文</a>
</p>

![App Preview](screenshot.png)

An automation script application based on computer vision, Seeed Studio Xiao ESP32S3, CircuitPython, and a PySide6 GUI, providing intuitive operations and route recording features.

The primary goal is to build a **keyboard and mouse with "ears"**, capable of matching screen elements (listening) while simulating keystrokes or mouse movements.

## ✨ Key Features
- **Modern Control Center**: A dark-themed GUI.
- **Route Recording & Replay**: Supports manual recording of grinding loops and replays them with high-precision time series.
- **Full Automation Functions**:
  - **Auto Grind (State Machine Architecture)**:
    - Designed with a **Finite State Machine (FSM)**, separating grinding behaviors into modular states: Stationary, Walker, Wander, RuneSolver, and Pause.
    - **Stack-based Interrupt**: When unsafe conditions are detected (e.g., player nearby, rune appears, focus lost), the Machine pushes the current state onto a stack and transitions to an interrupt state. Once the environment is safe, the Machine pops the previous state and resumes seamlessly — preserving internal state such as remaining cooldown time.
  - **Daily Automations**: Automatically processes daily/weekly quests, Legion coins, Fairy Bros' Daily Gift (HD), Maple Points (Milestone), Auction House, Home, and more.
  - **Utility Tools**: Monster Collection, Gear Extraction, and automatic warehouse secondary password entry.

## 🛠️ Requirements & Installation

1. **Hardware Preparation**:
   - Please refer to [How to Prepare Hardware](how_to_circuitpython_EN.md)
2. **Run the Executable File (.exe)**
3. **Or Run Locally with Python**:
   - Install Python 3.11+
   - Create and activate a virtual environment:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the main script:
     ```bash
     python main.py
     ```
4. **Auto-Configuration**:
   - After launching, click the **⚙️ Settings button** next to each task to configure hotkeys, capture template images, and record routes.

## 🏗️ Software Architecture & Flow

The architecture uses a **Multi-threading** design to ensure the GUI remains responsive while running automation tasks safely.

```mermaid
graph TD
    User[User] -->|Click Button| GUI["GUI (PySide6)"]
    
    subgraph "Frontend (Main Thread)"
        GUI -->|Start Task| TaskManager["TaskManager"]
        GUI -->|Press Stop| TaskManager
        LogSignal["Log Signal Bridge"] -.->|Update Text| GUI
    end

    subgraph "Backend (Worker Thread)"
        TaskManager -->|Spawn Thread| Worker["Worker Thread"]
        Worker -->|Execute Logic| Script["MapleScript"]

        subgraph "All Script"
            Daily["Daily Task Scripts\n(Linear Scripts)"]
            subgraph "Grinding State Machine (MapleMachine)"
                FSM["State Machine Manager (Machine)"]
                State["Stationary / Walker / Wander / RuneSolver"]
                PauseState["Pause / RuneSolver"]
                FSM -->|"check_status() → string key"| State
                FSM -->|"Unsafe detected: push state to stack"| PauseState
                PauseState -.->|"Safe restored: pop state from stack"| FSM
            end
        end

        Script -->|"Daily / Legion / Auction...\n(Linear Scripts)"| Daily
        Script -->|MapleGrind Start| FSM
        Script -->|Report Progress| LogSignal
        Script -->|Check Stop Signal| StopEvent{"Is Stopped?"}
        Script -->|Computer Vision| Vision["Computer Vision (OpenCV)"]
        Script -->|Control Commands| Controller["Xiao Controller"]
    end

    subgraph "Hardware Layer"
        Controller ==>|USB Serial| XiaoBoard["Xiao ESP32S3"]
        XiaoBoard ==>|HID| Game["MapleStory Window"]
    end
```

> [!NOTE]
> For detailed state transitions, cooldown mechanics, and the stack-based pause logic, please refer to the [State Machine Documentation](src/states/README_EN.md).

## 🔌 Hardware Interaction Principle
```mermaid
%%{init: {'theme': 'forest'} }%%
graph LR;

step1["Xiao initialized as Keyboard/Mouse"]

step2["PC recognizes screen"]

step3["Store into list"]

step4["Pop & Send to Xiao"]

step5["Xiao presses key"]

step6["PC receives"]

step7["Xiao moves mouse"]

step8["PC calculates distance to move mouse"]

step9["Scroll wheel needs to scroll up/down"]

step10["Xiao scrolls up/down"]

step11["Xiao clicks"]

step12["Key to be pressed"]

step13["Key to be held then released"]

step14["Xiao holds & releases"]

%% Flowlines -->
step1 ==> step2
step1 ==> step8
step1 ==> step9
step1 ==> step12
step1 ==> step13
step5 ==> step6
step14 ==> step6
step11 ==> step6
step10 ==> step6

subgraph Keyboard
step2 ==> step3 ==> step4 ==> step5
step12 ==> step5
step13 ==> step14
end
subgraph Mouse
step8 ==> step7 ==> step11
step9 ==> step10
end
```

## 📄 License & Disclaimer

This project is licensed under the [GNU General Public License v3.0](LICENSE.txt). Before using this software, please make sure to read and agree to the **Disclaimer** listed in the `LICENSE.txt` file.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=abc21086999/maple_script&type=date&legend=top-left)](https://www.star-history.com/#abc21086999/maple_script&type=date&legend=top-left)
