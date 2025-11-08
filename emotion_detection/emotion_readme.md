# 情緒檢測系統 - 使用指南

基於 DeepFace 的高準確度情緒識別系統

---

## 🎯 系統特點

✅ **基於 DeepFace 官方 API** - 使用最佳實踐  
✅ **物件導向設計** - 代碼簡潔易維護  
✅ **支援多種檢測器** - 靈活選擇速度與準確度  
✅ **智能平滑算法** - 指數移動平均,減少誤判  
✅ **美觀的視覺界面** - 實時顯示情緒分數  
✅ **易於配置** - 所有參數集中在文件開頭  

---

## 📦 安裝依賴

### 基本依賴 (必須)
```bash
pip install opencv-python deepface pillow numpy
```

### 可選檢測器 (提高準確度)
```bash
# MTCNN (推薦 - 準確度高,速度適中)
pip install mtcnn

# RetinaFace (最高準確度,但較慢)
pip install retina-face

# MediaPipe (Google 方案)
pip install mediapipe
```

---

## 🚀 快速開始

### 方法 1: 使用默認配置 (推薦新手)

直接運行:
```bash
python emotion.py
```

### 方法 2: 自定義配置

1. 打開 `emotion.py`
2. 修改文件開頭的配置區域 (第 15-28 行):
```python
# 檢測器選擇
DETECTOR_BACKEND = 'opencv'  # 改為 'mtcnn' 提高準確度

# 平滑窗口
SMOOTH_WINDOW = 15  # 建議 10-20

# 置信度閾值
CONFIDENCE_THRESHOLD = 30  # 建議 25-40
```

3. 運行程序:
```bash
python emotion.py
```

---

## ⚙️ 配置說明

### 檢測器選擇 (DETECTOR_BACKEND)

在 `emotion.py` 第 18 行修改:

| 檢測器 | 速度 | 準確度 | 需要安裝 | 推薦場景 |
|--------|------|--------|----------|----------|
| `opencv` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ 無需 | 一般使用,光線良好 |
| `ssd` | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ 無需 | 需要速度 |
| `mtcnn` | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 需要 | **推薦 - 平衡之選** |
| `retinaface` | ⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 需要 | 最高準確度 |
| `mediapipe` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 需要 | Google 方案 |

### 關鍵參數說明

```python
# 1. 檢測器 (第 18 行)
DETECTOR_BACKEND = 'opencv'
# 推薦: 'mtcnn' (需安裝: pip install mtcnn)

# 2. 平滑窗口 (第 21 行)
SMOOTH_WINDOW = 15
# 作用: 對多幀結果平滑處理
# 越大: 越穩定但反應越慢
# 越小: 反應越快但可能抖動
# 建議: 10-20

# 3. 置信度閾值 (第 24 行)
CONFIDENCE_THRESHOLD = 30
# 作用: 只顯示置信度超過此值的情緒
# 越高: 越嚴格,誤判越少
# 越低: 越寬鬆,更容易顯示
# 建議: 25-40

# 4. 處理間隔 (第 27 行)
PROCESS_EVERY_N_FRAMES = 2
# 作用: 每 N 幀分析一次,提高性能
# opencv: 2-3
# mtcnn/retinaface: 4-5

# 5. 攝像頭解析度 (第 30-31 行)
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
# 高解析度: 更清晰,但可能較慢
# 低解析度 (640x480): 更快
```

---

## 🎨 界面說明

### 主顯示區域 (左上)
- 顯示當前主導情緒 (中文 + 表情符號)
- 顯示置信度百分比
- ✓ 標記表示高置信度 (>50%)

### 詳細分數 (右側)
- 顯示前 5 名情緒及其置信度
- 進度條視覺化
- 當前主導情緒以綠色高亮

### 狀態欄 (底部)
- 緩衝區填充狀態
- 當前使用的檢測器

---

## 💡 提高準確度的技巧

### 1. 硬體環境 🎥 (最重要!)

✅ **光線充足**
- 正面光最佳
- 避免逆光和強烈陰影
- 均勻照明效果最好

✅ **面部清晰**
- 正對攝像頭 (不要側臉)
- 距離 50-100 公分
- 確保面部完整在畫面中

✅ **背景簡單**
- 避免複雜背景
- 單色背景最佳

✅ **攝像頭質量**
- 720p 或以上
- 確保對焦清晰

### 2. 表情技巧 😊

✅ **表情明顯**
- 誇張的表情更容易識別
- 開心時**露齒笑**效果最好
- 生氣時皺眉 + 瞪眼

✅ **保持時間**
- 每個表情保持 2-3 秒
- 給系統時間穩定

✅ **避免快速切換**
- 不要快速變換表情
- 給系統反應時間

### 3. 軟體配置 ⚙️

#### 配置 A: 追求最高準確度
```python
DETECTOR_BACKEND = 'mtcnn'  # 或 'retinaface'
SMOOTH_WINDOW = 20
CONFIDENCE_THRESHOLD = 25
PROCESS_EVERY_N_FRAMES = 4
```
**說明**: 使用更準確的檢測器,增加平滑,降低閾值讓系統更容易顯示結果

#### 配置 B: 速度優先
```python
DETECTOR_BACKEND = 'opencv'
SMOOTH_WINDOW = 10
CONFIDENCE_THRESHOLD = 35
PROCESS_EVERY_N_FRAMES = 3
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
```
**說明**: 使用最快檢測器,降低解析度,提高閾值

#### 配置 C: 平衡推薦 ⭐
```python
DETECTOR_BACKEND = 'opencv'  # 如安裝了 mtcnn 可改用
SMOOTH_WINDOW = 15
CONFIDENCE_THRESHOLD = 30
PROCESS_EVERY_N_FRAMES = 2
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
```
**說明**: 默認配置,適合大多數情況

---

## 🔧 故障排除

### 問題 1: 把"開心"誤判成"難過" 😊→😢

**可能原因**:
- 笑容不夠明顯
- 光線不佳導致陰影
- 置信度閾值太低

**解決方案**:
1. **改善環境** (最重要):
   - 確保**露齒笑**
   - 改善光線 (打開燈,正面照明)
   - 保持表情 3 秒以上

2. **調整配置**:
```python
DETECTOR_BACKEND = 'mtcnn'  # 換用更準確的檢測器
SMOOTH_WINDOW = 20          # 增加平滑
CONFIDENCE_THRESHOLD = 35   # 提高閾值
```

3. **安裝更好的檢測器**:
```bash
pip install mtcnn
```

---

### 問題 2: 經常顯示"偵測中..." 🔍

**可能原因**:
- 置信度閾值太高
- 面部檢測不到
- 表情不夠明顯

**解決方案**:
1. **調整配置**:
```python
CONFIDENCE_THRESHOLD = 25  # 降低閾值
SMOOTH_WINDOW = 10         # 減少平滑窗口
```

2. **改善環境**:
   - 確保面部完整在畫面中
   - 改善光線
   - 調整攝像頭角度和距離

---

### 問題 3: 速度太慢/卡頓 🐌

**解決方案**:
```python
DETECTOR_BACKEND = 'opencv'      # 使用最快的檢測器
PROCESS_EVERY_N_FRAMES = 3       # 增加處理間隔
CAMERA_WIDTH = 640               # 降低解析度
CAMERA_HEIGHT = 480
SMOOTH_WINDOW = 10               # 減少窗口
```

---

### 問題 4: 檢測不到臉部 👤

**解決方案**:
1. **檢查環境**:
   - 確保面部正對攝像頭 (不要側臉)
   - 距離適中 (50-100 公分)
   - 改善光線 (打開燈光)
   - 移除遮擋物 (口罩、手、頭髮)

2. **換用更好的檢測器**:
```python
DETECTOR_BACKEND = 'mtcnn'  # 或 'retinaface'
```

---

### 問題 5: 情緒變化太快/抖動 ⚡

**解決方案**:
```python
SMOOTH_WINDOW = 20              # 大幅增加平滑
PROCESS_EVERY_N_FRAMES = 3      # 降低更新頻率
CONFIDENCE_THRESHOLD = 35       # 提高閾值
```

---

## 📊 DeepFace 情緒分類

DeepFace 識別 **7 種基本情緒**:

| 情緒 | 英文 | 中文 | 識別難度 | 建議 |
|------|------|------|----------|------|
| 😊 | happy | 開心 | ⭐ 容易 | **露齒笑**效果最好 |
| 😐 | neutral | 平靜 | ⭐ 容易 | 面無表情 |
| 😠 | angry | 生氣 | ⭐⭐ 中等 | 皺眉 + 瞪眼 |
| 😢 | sad | 難過 | ⭐⭐ 中等 | 嘴角下垂 + 眼神憂鬱 |
| 😲 | surprise | 驚訝 | ⭐⭐ 中等 | 張大嘴 + 瞪大眼 |
| 😨 | fear | 害怕 | ⭐⭐⭐ 困難 | 眼睛睜大 + 嘴微張 |
| 🤢 | disgust | 噁心 | ⭐⭐⭐ 困難 | 皺鼻子 + 撇嘴 |

**提示**: 
- happy 和 neutral 最容易識別 ✅
- fear 和 disgust 最困難 ⚠️
- 建議先測試 happy、neutral、sad 這三種

---

## 🏗️ 代碼結構

```
emotion.py
├── 配置區域 (第 15-34 行)
│   ├── DETECTOR_BACKEND      # 檢測器選擇
│   ├── SMOOTH_WINDOW         # 平滑窗口
│   ├── CONFIDENCE_THRESHOLD  # 置信度閾值
│   └── 其他參數...
│
├── 工具函數
│   ├── find_chinese_font()   # 尋找中文字體
│   └── draw_chinese_text()   # 繪製中文文字
│
├── EmotionDetector 類
│   ├── __init__()            # 初始化
│   ├── analyze_frame()       # 分析單幀
│   ├── get_smoothed_emotion() # 獲取平滑結果
│   ├── process_frame()       # 處理並標註
│   └── _draw_emotion_info()  # 繪製UI
│
└── main()                     # 主程序
```

---

## 📖 使用建議

### 對於初學者 👶

1. **使用默認配置** (opencv 檢測器)
2. **確保良好光線** (最重要!)
3. **表情明顯誇張** (特別是露齒笑)
4. **從 happy 開始測試** (最容易識別)

### 對於進階用戶 🎓

1. **安裝 MTCNN**:
```bash
pip install mtcnn
```

2. **在 emotion.py 中修改**:
```python
DETECTOR_BACKEND = 'mtcnn'
SMOOTH_WINDOW = 18
CONFIDENCE_THRESHOLD = 28
```

3. **根據結果微調參數**

### 對於追求極致準確度 🏆

1. **安裝 RetinaFace**:
```bash
pip install retina-face
```

2. **配置高性能參數**:
```python
DETECTOR_BACKEND = 'retinaface'
SMOOTH_WINDOW = 20
CONFIDENCE_THRESHOLD = 25
PROCESS_EVERY_N_FRAMES = 5
```

3. **使用高質量攝像頭** (1080p)
4. **專業打光設備**

---

## 🎓 技術細節

### 平滑算法
使用**指數加權移動平均** (Exponential Weighted Moving Average):
```python
weights = np.exp(np.linspace(0, 2, len(buffer)))
```
- 最近的幀權重更高
- 避免突然的情緒跳變
- 保持快速響應

### 置信度計算
- 對窗口內所有幀的情緒分數加權平均
- 只有當主導情緒分數 > 閾值才顯示
- 減少誤判和閃爍

### 性能優化
- 只在指定間隔分析情緒 (PROCESS_EVERY_N_FRAMES)
- 其他幀重用上次結果
- 平衡準確度和性能

---

## ❓ 常見問題 FAQ

**Q: 為什麼有時候會誤判?**  
A: 情緒識別基於統計模型,不可能 100% 準確。通過:
- 改善光線環境
- 表情更明顯
- 調高置信度閾值
- 使用更好的檢測器  
可以顯著減少誤判。

**Q: 需要什麼配置的電腦?**  
A: 
- **最低**: 4GB RAM, 集成顯卡 (使用 opencv)
- **推薦**: 8GB RAM, 獨立顯卡 (使用 mtcnn/retinaface)

**Q: 支援多人同時檢測嗎?**  
A: 目前版本只檢測最大的臉部。如需多人檢測,需要修改代碼。

**Q: 可以用於商業項目嗎?**  
A: DeepFace 使用 MIT License,可以商用。但請查看具體模型的授權。

**Q: 為什麼第一次運行很慢?**  
A: DeepFace 需要下載模型文件 (約 100-500MB),只有第一次會慢。

---

## 📚 參考資料

- **DeepFace GitHub**: https://github.com/serengil/deepface
- **DeepFace 論文**: Serengil & Ozpinar, 2020
- **情緒識別理論**: Ekman's Basic Emotions

---

## 🎯 快速調整指南

### 提高準確度
```python
DETECTOR_BACKEND = 'mtcnn'       # 換用更準確的檢測器
SMOOTH_WINDOW = 20               # 增加平滑
CONFIDENCE_THRESHOLD = 35        # 提高閾值 (減少誤判)
```

### 提高速度
```python
DETECTOR_BACKEND = 'opencv'      # 使用最快的檢測器
PROCESS_EVERY_N_FRAMES = 3       # 增加處理間隔
CAMERA_WIDTH = 640               # 降低解析度
CAMERA_HEIGHT = 480
```

### 更容易顯示結果
```python
CONFIDENCE_THRESHOLD = 25        # 降低閾值
SMOOTH_WINDOW = 10               # 減少平滑窗口
```

### 更穩定的結果
```python
SMOOTH_WINDOW = 20               # 增加平滑窗口
PROCESS_EVERY_N_FRAMES = 3       # 降低更新頻率
CONFIDENCE_THRESHOLD = 35        # 提高閾值
```

---

## 💪 下一步

1. **立即測試**: 運行 `python emotion.py`
2. **調整配置**: 根據效果修改 emotion.py 開頭的參數
3. **安裝更好的檢測器**: `pip install mtcnn`
4. **閱讀 DeepFace 文檔**: 了解更多進階用法

---

## ✨ 使用技巧總結

**記住三個關鍵**:
1. 💡 **光線充足** (正面光,避免逆光)
2. 😊 **表情明顯** (誇張,保持 2-3 秒)
3. ⚙️ **適當配置** (根據環境調整參數)

**祝你使用愉快! 🎉**

---

## 📝 更新日誌

### v2.0 (整合版)
- ✅ 整合 emotion.py 和 emotion_new.py
- ✅ 物件導向設計
- ✅ 配置參數集中在文件開頭
- ✅ 支援多種檢測器
- ✅ 改進的平滑算法
- ✅ 美化的界面
- ✅ 詳細的文檔

### v1.0 (原版)
- 基本的情緒檢測功能
- Haar Cascade 檢測

