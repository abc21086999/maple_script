# MapleScript
一個基於視覺辨識、Seeed Studio Xiao ESP32S3、CircuitPython的腳本程式。採模組化與設定檔驅動架構，大幅提升擴充性與易用性。

主要目的是打造**有耳朵的鍵盤、滑鼠**，能夠一邊聽，一邊按下按鍵或是一邊移動滑鼠。

## 目前功能
- **自動練功 (Auto Grind)**：依據小地圖判斷位置並執行巡邏路徑。
- **每日任務全自動**：
  - 開始 / 完成每日任務
  - 每日 Boss (如：炎魔、暴君、希拉、阿卡伊農等)
  - 領取戰地硬幣
  - 領取 HD 硬幣 / 獎勵
  - 領取里程
  - 完成師徒任務
  - 小屋每日對話
  - 怪物蒐藏
- **輔助功能**：
  - 自動分解裝備
  - 拍賣場自動領錢 / 重新上架
  - 打開倉庫並自動輸入第二組密碼
  - 跳舞機活動自動化

## 環境需求與安裝

1.  **硬體準備**：
    - 需要一塊 **能刷入CircuitPython** 的開發板。
    - 將 `XiaoCode/` 資料夾內的程式碼燒錄至開發板。
2.  **軟體安裝**：
    - 安裝 Python 3.10+。
    - 安裝相依套件：
      ```bash
      pip install -r requirements.txt
      ```
    - 設定 `config/config.yaml` (技能按鍵、圖片路徑) 與 `.env` (敏感資料)。

## 使用方式

請在專案根目錄下開啟終端機 (Terminal / CMD)，依據需求執行以下指令：

| 功能 | 指令 | 說明                   |
| :--- | :--- |:---------------------|
| **自動練功** | `python -m src grind` | 執行自動打怪腳本             |
| **每日任務** | `python -m src daily` | 執行每日例行事項 (戰地、里程、HD等) |
| **每日 Boss** | `python -m src daily_boss` | 自動挑戰每日 Boss          |
| **怪物蒐藏** | `python -m src collection` | 領取怪物蒐藏               |
| **倉庫存取** | `python -m src storage` | 自動輸入倉庫密碼             |
| **跳舞機** | `python -m src dance` | 執行跳舞機活動腳本            |

## 整體流程
```mermaid
%%{init: {'theme': 'forest'} }%%
graph LR;

step1([Xiao初始化為鍵盤、滑鼠])

step2([電腦辨識畫面])

step3([存入list])

step4([取出傳送給Xiao])

step5([Xiao按下按鍵])

step6([電腦收到])

step7([Xiao移動滑鼠])

step8([電腦計算滑鼠要移動的距離])

step9([滑鼠滾輪要上下滾動])

step10([Xiao滾輪上下滑動])

step11([Xiao點擊])

step12([有要按下的按鍵])

step13([有要長壓之後放開的按鍵])

step14([Xiao長壓後放開])

%% 流程線 -->
step1 ==> step2
step1 ==> step8
step1 ==> step9
step1 ==> step12
step1 ==> step13
step5 ==> step6
step14 ==> step6
step11 ==> step6
step10 ==> step6

subgraph 鍵盤
step2 ==> step3 ==> step4 ==> step5
step12 ==> step5
step13 ==> step14
end
subgraph 滑鼠
step8 ==> step7 ==> step11
step9 ==> step10
end
```

### 視覺辨識
視覺辨識採用Pyautogui：先將要辨識的區域截圖，並將要比對的圖片用Pillow吃進記憶體以減少IO開銷，最後於截圖上進行比對

有比對到想要的東西，就再進行按下對應的按鍵，或是將滑鼠移動過去的操作

### 與CircuitPython的溝通
硬體採用**Seeed Studio Xiao ESP32S3**，刷入CircuitPython，並且初始化為鍵盤、滑鼠之後持續聆聽USB送過來的訊號


