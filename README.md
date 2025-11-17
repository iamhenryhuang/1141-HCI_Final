# 手勢識別與追蹤系統

這是一個基於 MediaPipe 和 OpenCV 的即時手勢識別系統，能夠識別多種手勢，並對不雅手勢自動進行馬賽克處理。系統還具備**不雅手勢追蹤功能**，當累積達到閾值時，會自動啟用臉部馬賽克。

## 功能特色

-  **即時手勢識別**：支援多種手勢識別，包括讚/倒讚、OK 手勢、搖滾手勢、拳頭等
-  **自動馬賽克處理**：偵測到不雅手勢時自動進行馬賽克模糊處理
-  **不雅手勢追蹤**：系統會自動記錄不雅手勢次數
-  **臉部馬賽克懲罰**：當累積 5 次不雅手勢後，自動啟用臉部馬賽克功能
-  **靈活配置**：所有參數都可透過 `config.py` 輕鬆調整
-  **高精準度**：使用 MediaPipe 的手部追蹤技術，識別準確度高
-  **高效能**：即時處理，延遲低

## 支援的手勢

### 一般手勢
- **good**：豎起大拇指（讚）
- **ROCK!**：搖滾手勢（食指與小指伸直）
- **fist**：拳頭

### 不雅手勢（會被馬賽克處理並計數）
- **bad!!!**：倒讚（大拇指朝下）
- **no!!!**：比中指
- **thumb_mid_pinky**：大拇指+中指+小指同時伸直
- **ok**：OK 手勢（在本系統中被列為敏感手勢）

## 不雅手勢追蹤機制

系統會自動追蹤用戶比出的不雅手勢次數，並根據累積次數採取相應措施：

- **不雅手勢 1-4 次**：只對手部進行馬賽克處理
- **不雅手勢 ≥5 次**：手部和臉部都會進行馬賽克處理
- **按 q 離開**：自動重置計數器

### 畫面資訊顯示

程式運行時，左上角會顯示：
- `Bad Gestures: X/5` - 當前累積次數
- `Status: Normal (X warnings left)` (綠色) - 正常狀態，顯示剩餘警告次數
- `Status: FACE MOSAIC ON` (紅色) - 臉部馬賽克已啟用

## 專案結構

```
hci_final/
├── finger_detection/          # 手勢識別主模組
│   ├── main.py               # 主程式入口
│   ├── utils.py              # 工具函數模組（角度計算、手勢判定）
│   ├── backend.py            # 後台追蹤管理（不雅手勢計數、臉部馬賽克控制）
│   ├── config.py             # 配置檔案
│   ├── gesture_log.json      # 手勢記錄檔案（自動生成）
│   └── requirements.txt      # Python 依賴套件
├── face_detection/           # 臉部偵測模組
├── emotion_detection/        # 情緒偵測模組
└── README.md                 # 本說明文件
```

## 安裝步驟

### 1. 確認 Python 版本

請確保您的系統已安裝 Python 3.8 或更高版本：

```bash
python --version
```

### 2. 安裝依賴套件

在專案目錄下執行：

```bash
pip install -r requirements.txt
```

主要依賴套件包括：
- `mediapipe`：Google 的機器學習解決方案，用於手部追蹤
- `opencv-python`：影像處理函式庫
- `numpy`：數值運算函式庫

## 使用方法

### 基本使用

進入 `finger_detection` 目錄並執行主程式：

```bash
cd finger_detection
python main.py
```

### 操作說明

1. 程式啟動後會自動開啟攝影機，並開始即時識別手勢
2. 偵測到不雅手勢時會自動計數並對手部進行馬賽克處理
3. 累積達到 5 次不雅手勢後會啟用臉部馬賽克功能
4. 畫面左上角會即時顯示統計資訊
5. 按 `q` 鍵退出程式（計數器會自動重置）

### 退出程式

在視窗中按下 `q` 鍵即可退出程式，系統會自動重置計數器。

## 配置說明

所有可調整的參數都在 `finger_detection/config.py` 中，您可以根據需求修改：

### 攝影機設定

```python
CAMERA_INDEX = 0        # 攝影機編號（0 為預設攝影機）
FRAME_WIDTH = 720       # 影像寬度
FRAME_HEIGHT = 540      # 影像高度
```

### MediaPipe 參數

```python
MODEL_COMPLEXITY = 0              # 模型複雜度（0: 快速, 1: 準確但較慢）
MIN_DETECTION_CONFIDENCE = 0.5    # 手部偵測信心閾值（0.0-1.0）
MIN_TRACKING_CONFIDENCE = 0.5     # 手部追蹤信心閾值（0.0-1.0）
```

### 手勢識別參數

```python
FINGER_BEND_THRESHOLD = 50        # 手指彎曲判定閾值（角度）
```

### 馬賽克效果設定

```python
BLACKLIST_GESTURES = ('no!!!', 'bad!!!', 'thumb_mid_pinky', 'ok')  # 需要馬賽克的手勢
DEBOUNCE_FRAMES = 3               # 連續出現多少幀才觸發馬賽克
BBOX_SMOOTH_ALPHA = 0.65          # 邊界框平滑係數（0.0-1.0）
```

### 不雅手勢追蹤設定

```python
BAD_GESTURE_THRESHOLD = 5         # 觸發臉部馬賽克的不雅手勢次數閾值
GESTURE_LOG_FILE = 'gesture_log.json'  # 手勢記錄檔案
```

### 臉部偵測與馬賽克設定

```python
FACE_SCALE_FACTOR = 1.1           # 臉部偵測縮放比例
FACE_MIN_NEIGHBORS = 5            # 最小鄰居數（越大越嚴格）
FACE_MIN_SIZE = (30, 30)          # 最小臉部尺寸
FACE_MOSAIC_LEVEL = 15            # 臉部馬賽克效果等級（數字越大越粗糙）
```

### 顯示設定

```python
WINDOW_NAME = 'Hand Gesture Recognition'  # 視窗名稱
TEXT_FONT_SCALE = 5                       # 文字大小
WARNING_TEXT = 'BAD!!!'                   # 警告文字
EXIT_KEY = 'q'                            # 退出按鍵
```

## 技術說明

### 手勢識別原理

1. **手部偵測**：使用 MediaPipe 偵測手部的 21 個關鍵點
2. **角度計算**：根據關鍵點座標計算每根手指的彎曲角度
3. **手勢判定**：根據五根手指的角度組合判定手勢類型
4. **方向判定**：對於讚/倒讚手勢，額外判斷大拇指的朝向

### 馬賽克處理流程

1. **手勢確認**：連續數幀偵測到同一不雅手勢才觸發（避免誤判）
2. **區域計算**：計算手部的凸包（Convex Hull）並加上邊距
3. **邊界平滑**：使用指數移動平均（EMA）平滑邊界框，避免抖動
4. **馬賽克生成**：將區域縮小再放大，產生像素化效果
5. **警告顯示**：在馬賽克區域上方顯示警告文字

### 不雅手勢追蹤機制

1. **記錄管理**：使用 `backend.py` 中的 `GestureTracker` 類別管理計數
2. **持久化儲存**：將計數記錄儲存在 `gesture_log.json` 檔案中
3. **每日重置**：系統會檢查日期，新的一天自動重置計數器
4. **臉部偵測**：達到閾值後，使用 OpenCV 的 Haar Cascade 進行臉部偵測
5. **臉部馬賽克**：對偵測到的臉部區域應用馬賽克效果

## 疑難排解

### 攝影機無法開啟

- 確認攝影機已正確連接
- 檢查其他程式是否正在使用攝影機
- 嘗試修改 `config.py` 中的 `CAMERA_INDEX`（改為 1、2 等）

### 識別不準確

- 增加 `MIN_DETECTION_CONFIDENCE` 和 `MIN_TRACKING_CONFIDENCE` 的值
- 調整 `FINGER_BEND_THRESHOLD` 參數
- 改善光線條件
- 確保手部完整出現在畫面中

### 馬賽克過於敏感

- 增加 `DEBOUNCE_FRAMES` 的值（需要更多連續幀才觸發）
- 調整 `BLACKLIST_GESTURES`，移除不需要馬賽克的手勢

### 馬賽克抖動嚴重

- 增加 `BBOX_SMOOTH_ALPHA` 的值（更平滑但反應稍慢）
- 減少 `DEBOUNCE_FRAMES` 避免延遲過大

### 臉部馬賽克無法正常工作

- 確認 OpenCV 已正確安裝
- 檢查 Haar Cascade 檔案是否存在
- 調整 `FACE_SCALE_FACTOR` 和 `FACE_MIN_NEIGHBORS` 參數
- 改善光線條件，確保臉部清晰可見

### 想調整不雅手勢閾值

- 修改 `config.py` 中的 `BAD_GESTURE_THRESHOLD` 參數
- 預設為 5 次，可根據需求調整為其他數值

### 計數器未重置

- 確保按 `q` 鍵正常退出程式
- 如需手動重置，可刪除 `gesture_log.json` 檔案

## 系統需求

- **作業系統**：Windows 10/11、macOS 10.14+、Linux
- **Python**：3.8 或更高版本
- **記憶體**：建議 4GB 以上
- **攝影機**：任何 USB 或內建攝影機