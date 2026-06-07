<p align="center">
  <a href="how_to_circuitpython_EN.md">English</a> | <a href="how_to_circuitpython.md">繁體中文</a>
</p>

## 📦 Hardware Setup (Required for First-time Use)

> Don't worry if you have never used a microcontroller before—just follow the steps below!

## 🛠️ Requirements

### Hardware
- **Seeed Studio XIAO Series Board** (XIAO RP2040 or XIAO SAMD21 is recommended)
- USB Cable (Type-C)

### Software
- Python 3.10+
- Windows 10 / 11

### Step 1: Purchase the Development Board

Purchase the [Seeed Studio XIAO RP2040](https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html). It is widely available on Amazon, the official Seeed Studio Store, DigiKey, Mouser, or local hobbyist electronic shops for around $5–$8 USD.

### Step 2: Flash CircuitPython

1. Go to the [CircuitPython Official Website](https://circuitpython.org/downloads) and search for your development board model.
2. Download the latest `.uf2` firmware file.
3. Connect the development board to your computer using a USB cable.
4. **Enter Bootloader Mode**:
   - XIAO RP2040: Press and hold the `BOOT` button, press the `RESET` button once, then release both buttons.
   - A USB flash drive named `RPI-RP2` will appear on your computer.
5. **Directly copy** the downloaded `.uf2` file into this flash drive.
6. Once the copy is complete, the board will restart automatically, and the drive's name will change to `CIRCUITPY`.
7. **[Or refer to the official tutorial](https://wiki.seeedstudio.com/XIAO-RP2040-with-CircuitPython/)**

### Step 3: Install Required Libraries

1. Go to the [CircuitPython Library Bundle](https://circuitpython.org/libraries) and download the library bundle matching your CircuitPython version.
2. Extract the downloaded zip file, and copy the following folder to the `CIRCUITPY/lib/` directory:
   - `adafruit_hid/`

### Step 4: Configure USB CDC (Important!)

CircuitPython does not enable serial data communication by default. You need to configure it manually:

Create (or edit) a file named `boot.py` in the root directory of the `CIRCUITPY` drive, with the following content:

```python
import usb_cdc
usb_cdc.enable(console=True, data=False)
```

After saving the file, **press the RESET button on the board** to apply the configuration.

### Step 5: Copy Firmware Code

Copy the `code/code_for_xiao.py` file from this project to the root directory of the `CIRCUITPY` drive, renaming it to replace the original `code.py`.

Once copied and saved, the board will automatically run the code. The serial monitor should display:
```
XIAO initialized, waiting for commands...
```

### Step 6: Configure Connection Serial Number

Open MapleScript, click `Hardware Settings` in the GUI, and you can select your RP2040 to bind it as the hardware keyboard and mouse for MapleScript.
