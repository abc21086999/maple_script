# MapleScript
一個基於視覺辨識、Seeed Studio Xiao ESP32S3、CircuitPython的腳本程式。

主要目的是打造**有耳朵的鍵盤**，能夠一邊聽，一邊按下按鍵

## 整體流程
```mermaid
%%{init: {'theme': 'forest'} }%%
graph LR;

%% 第一步 []
step1[Xiao初始化為鍵盤]

%% 第二步 []
step2[電腦辨識畫面]

%% 第三步 []
step3[存入deque]

%% 第四步 []
step4[取出傳送給Xiao]

%% 第五步 []
step5[Xiao按下按鍵]

%% 第六步 []
step6[電腦收到]

%% 流程線 -->
step1 --> step2 --> step3 --> step4 --> step5 --> step6 --> step2
```

### 視覺辨識
視覺辨識採用Pyautogui：先將要辨識的區域截圖，並將要比對的圖片用Pillow吃進記憶體以減少IO開銷，最後於截圖上進行比對

### 與CircuitPython的溝通
硬體採用**Seeed Studio Xiao ESP32S3**，刷入CircuitPython，並且初始化為鍵盤之後持續聆聽USB送過來的訊號

### TODO:
- 看一下為什麼不能用`usb_cdc.data`溝通
- 其他動作可能要繼承MapleScript class 之後來操作

