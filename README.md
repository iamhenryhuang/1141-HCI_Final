## 手勢識別與追蹤系統

這是一個基於 MediaPipe 和 OpenCV 的即時手勢識別系統，能夠識別多種手勢，並對不雅手勢自動進行馬賽克處理。系統還具備**不雅手勢追蹤功能**，當累積達到閾值時，會自動啟用臉部馬賽克。

## 功能特色

-  **即時手勢識別**：支援多種手勢識別，包括讚/倒讚、OK 手勢、搖滾手勢、拳頭等
-  **自動馬賽克處理**：偵測到不雅手勢時自動進行馬賽克模糊處理
-  **不雅手勢追蹤**：系統會自動記錄不雅手勢次數
-  **臉部馬賽克懲罰**：當累積 5 次不雅手勢後，自動啟用臉部馬賽克功能

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
│   ├── main.py                # 手勢偵測主程式
│   ├── backend.py             # 不雅手勢計數與狀態管理
│   ├── config.py              # 參數設定（攝影機、門檻值、馬賽克強度等）
│   ├── geometry.py            # 手指角度與幾何運算
│   ├── gesture_recognizer.py  # 手勢分類邏輯（讚、倒讚、ROCK!、OK 等）
│   ├── visualizer.py          # 畫面繪製與手部／臉部馬賽克
│   ├── gesture_log.json       # 每日不雅手勢統計（自動產生）
│   └── requirements.txt       # finger_detection 模組單獨依賴（選用）
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

（手勢分類的實作主要在 `gesture_recognizer.py`，角度計算在 `geometry.py`）

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