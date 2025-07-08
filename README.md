# MapleScript
一個基於視覺辨識與Seeed Studio Xiao ESP32S3的腳本程式。

## 整體流程
```mermaid
%%{init: {'theme': 'forest'} }%%
graph LR;

%% 第一步 []
step1[外接裝置在通電時初始化為鍵盤]

%% 第二步 []
step2[螢幕上辨識技能是否有準備好]

%% 第三步 []
step3[將按鍵傳送給裝有CircuitPython的外接裝置]

%% 第四步 [//]
step4[/外接裝置收到要按的按鍵將同個按鍵按下/]

%% 第五步 []
step5[電腦收到外接裝置傳送過來的按鍵訊號]

%% 流程線 -->
step1 --> step2 --> step3 --> step4 --> step5 --> step2
```

### 視覺辨識
視覺辨識採用Pyautogui：先將要辨識的區域截圖，並將要比對的圖片用Pillow吃進記憶體以減少IO開銷，最後於截圖上進行比對

### 與CircuitPython的溝通
硬體採用**Seeed Studio Xiao ESP32S3**，刷入CircuitPython，並且初始化為鍵盤之後持續聆聽USB送過來的訊號

