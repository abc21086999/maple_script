## 📦 硬體設定（第一次使用必做）

> 如果你從來沒碰過微控制器也沒關係，照著步驟做就好！

## 🛠️ 需要準備的東西

### 硬體
- **Seeed Studio XIAO 系列開發板**（建議使用 XIAO RP2040 或 XIAO SAMD21）
- USB 傳輸線（Type-C）

### 軟體
- Python 3.10+
- Windows 10 / 11

### 第一步：購買開發板

前往購買 [Seeed Studio XIAO RP2040](https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html)，台灣各大電子材料行或蝦皮都有販售，價格約 200-300 元台幣。

### 第二步：刷入 CircuitPython

1. 前往 [CircuitPython 官網](https://circuitpython.org/downloads) 搜尋你的開發板型號
2. 下載最新版的 `.uf2` 韌體檔案
3. 將開發板用 USB 連接電腦
4. **進入 Bootloader 模式**：
   - XIAO RP2040：按住 `BOOT` 鍵不放，再按一下 `RESET` 鍵，放開兩個按鍵
   - 電腦上會出現一個名為 `RPI-RP2` 的隨身碟
5. 將下載的 `.uf2` 檔案**直接複製**進這個隨身碟
6. 複製完成後開發板會自動重啟，隨身碟名稱會變成 `CIRCUITPY`
7. **[或是查看官方版本的教學](https://wiki.seeedstudio.com/cn/XIAO-RP2040-with-CircuitPython/)**

### 第三步：安裝必要的函式庫

1. 前往 [CircuitPython Library Bundle](https://circuitpython.org/libraries) 下載對應版本的函式庫包
2. 解壓縮後，將以下資料夾複製到 `CIRCUITPY/lib/` 目錄下：
   - `adafruit_hid/`

### 第四步：設定 USB CDC（重要！）

CircuitPython 預設不會開啟序列通訊，需要手動設定：

在 `CIRCUITPY/` 根目錄建立（或編輯）`boot.py`，內容如下：

```python
import usb_cdc
usb_cdc.enable(console=True, data=False)
```

存檔後，**按一下開發板的 RESET 鍵**讓設定生效。

### 第五步：複製韌體程式碼

將專案中的 `code/code_for_xiao.py` 複製到 `CIRCUITPY/` 根目錄，覆蓋原有的 `code.py`。

複製完成並且存檔後開發板會自動執行程式，序列埠監視器應該會看到：
```
XIAO 已啟動，等待指令...
```

### 第六步：設定連接序號

打開MapleScript之後，點擊`硬體連線設定`，就能夠將你的RP2040指定為MapleScript使用的鍵盤滑鼠。