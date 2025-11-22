# MapleScript
一個基於視覺辨識、Seeed Studio Xiao ESP32S3、CircuitPython的腳本程式。本專案採模組化與設定檔驅動架構，大幅提升擴充性與易用性。

主要目的是打造**有耳朵的鍵盤、滑鼠**，能夠一邊聽，一邊按下按鍵或是一邊移動滑鼠

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

### 目前功能：
- 開始 / 完成每日任務
- 怪物蒐藏
- 領取戰地硬幣
- 自動分解裝備
- 拍賣領/重新上架東西
- 領取HD
- 領取里程
- 完成師徒
- 小屋每日對話
- 打開倉庫輸入第二組密碼
- 每日Boss (例如炎魔、暴君、希拉)
- 跳舞機活動

