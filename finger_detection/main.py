"""
手勢識別主程式 - 最終修正版本 (只替換臉部馬賽克邏輯)
功能：
1. 即時偵測不雅手勢並碼手（原邏輯）。
2. 達到閾值後，啟用穩定、持續的臉部追蹤馬賽克（新邏輯）。
"""

import cv2
import mediapipe as mp
import numpy as np
# 假設這些工具函式和設定檔案都存在
from utils import hand_angle, hand_pos 
from backend import GestureTracker
from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    MODEL_COMPLEXITY, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE,
    BLACKLIST_GESTURES, DEBOUNCE_FRAMES,
    BBOX_PADDING_RATIO, BBOX_EXTRA_PADDING, BBOX_MIN_DIMENSION,
    BBOX_SMOOTH_ALPHA,
    MOSAIC_DOWN_SAMPLE_MIN, MOSAIC_DOWN_SAMPLE_MAX, MOSAIC_DOWN_SAMPLE_DIVISOR,
    WINDOW_NAME, TEXT_FONT_SCALE, TEXT_THICKNESS, TEXT_COLOR, TEXT_POSITION,
    WARNING_TEXT, WARNING_FONT_SCALE, WARNING_THICKNESS, WARNING_COLOR,
    WARNING_BG_COLOR, WARNING_BG_PADDING,
    BAD_GESTURE_THRESHOLD, GESTURE_LOG_FILE,
    FACE_CASCADE_NAME, 
    FACE_MOSAIC_LEVEL, FACE_MOSAIC_WARNING_TEXT, FACE_MOSAIC_WARNING_COLOR,
    FACE_MOSAIC_WARNING_FONT_SCALE, FACE_MOSAIC_WARNING_THICKNESS,
    EXIT_KEY
)

# ====== 新增：馬賽克輔助函式（用於新的臉部邏輯，取代舊的 in-line 邏輯） ======
def apply_mosaic(frame, x1, y1, x2, y2, level):
    """對指定的邊界框區域應用馬賽克效果"""
    
    # 確保座標有效且在範圍內
    h, w, _ = frame.shape
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)
    
    if x2 <= x1 or y2 <= y1:
        return

    roi = frame[y1:y2, x1:x2]
    # 縮小
    small = cv2.resize(roi, (max(1, roi.shape[1]//level), max(1, roi.shape[0]//level)), interpolation=cv2.INTER_LINEAR)
    # 放大（馬賽克效果）
    mosaic = cv2.resize(small, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_NEAREST)
    frame[y1:y2, x1:x2] = mosaic
# =========================================================================

def main():
    """主程式入口"""
    # 初始化後台追蹤器
    tracker = GestureTracker(data_file=GESTURE_LOG_FILE)
    tracker.threshold = BAD_GESTURE_THRESHOLD
    
    # 顯示初始統計資訊
    stats = tracker.get_statistics()
    
    # 初始化 MediaPipe 手部偵測工具
    mp_hands = mp.solutions.hands
    
    # ====== 新增：MediaPipe 臉部網格初始化 (用於追蹤器初始化) ======
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1, 
        min_detection_confidence=0.5, 
        static_image_mode=False # 允許追蹤模式
    )
    # ===============================================

    # 初始化攝影機
    cap = cv2.VideoCapture(CAMERA_INDEX)
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    lineType = cv2.LINE_AA

    # 原有的 Haar Cascade 不再使用，因此移除相關初始化
    # cascade_path = cv2.data.haarcascades + FACE_CASCADE_NAME
    # face_cascade = cv2.CascadeClassifier(cascade_path)
    # if not face_cascade.empty(): face_cascade = None # 移除

    # ====== 新增：臉部追蹤狀態變數（用於替換 Haar Cascade 邏輯） ======
    face_tracker = None
    tracking = False
    bbox_fixed = None  # 紀錄追蹤目標的固定馬賽克尺寸 (x, y, w, h)
    mask_duration = 50 
    mask_timer = 0
    # =========================================================

    print("=" * 50)
    print("手勢識別系統啟動中 (已優化臉部馬賽克追蹤)...")
    # ... (省略初始化印出，保持原樣) ...
    print("=" * 50)

    # 啟用 MediaPipe 手部偵測
    with mp_hands.Hands(
        model_complexity=MODEL_COMPLEXITY,
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE) as hands:

        if not cap.isOpened():
            print("錯誤：無法開啟攝影機")
            return

        w, h = FRAME_WIDTH, FRAME_HEIGHT

        prev_bbox = None
        alpha = BBOX_SMOOTH_ALPHA

        gesture_buffer_text = ''
        gesture_buffer_count = 0
        current_gesture_logged = False

        while True:
            ret, img = cap.read()
            
            if not ret:
                print("錯誤：無法讀取影像")
                break
                
            img = cv2.resize(img, (w, h))

            # 轉換成 RGB 色彩供 MediaPipe 處理
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # --- 核心手勢偵測處理 (完全保留原程式碼邏輯) ---
            results = hands.process(img_rgb) # **手勢偵測**

            # 如果偵測到手部
            if results.multi_hand_landmarks:
                detections = [] 
                
                # ----------------------------------------------------
                # [原程式碼：手部關鍵點取得、手勢識別、填充 detections 列表]
                # ----------------------------------------------------
                for hand_landmarks in results.multi_hand_landmarks:
                    finger_points = []
                    fx = []
                    fy = []
                    for i in hand_landmarks.landmark:
                        x = int(i.x * w)
                        y = int(i.y * h)
                        finger_points.append((x, y))
                        fx.append(x)
                        fy.append(y)

                    if finger_points:
                        finger_angle = hand_angle(finger_points)
                        text = hand_pos(finger_angle, finger_points)
                        detections.append({'text': text, 'finger_points': finger_points, 'fx': fx, 'fy': fy})

                # [原程式碼：Debounce 邏輯]
                frame_candidates = [d['text'] for d in detections if d['text'] in BLACKLIST_GESTURES]
                if frame_candidates:
                    candidate = max(set(frame_candidates), key=frame_candidates.count)
                    if candidate == gesture_buffer_text:
                        gesture_buffer_count += 1
                        if gesture_buffer_count >= DEBOUNCE_FRAMES and not current_gesture_logged:
                            tracker.add_bad_gesture(candidate)
                            current_gesture_logged = True
                    else:
                        gesture_buffer_text = candidate
                        gesture_buffer_count = 1
                        current_gesture_logged = False
                else:
                    gesture_buffer_text = ''
                    gesture_buffer_count = 0
                    current_gesture_logged = False

                # [原程式碼：手勢馬賽克和警告文字繪製]
                for d in detections:
                    text = d['text']
                    finger_points = d['finger_points']
                    fx = d['fx']
                    fy = d['fy']
                    
                    should_mosaic = (text in BLACKLIST_GESTURES and 
                                    text == gesture_buffer_text and 
                                    gesture_buffer_count >= DEBOUNCE_FRAMES)
                    
                    if should_mosaic:
                        # ----------------------------------------------------
                        # (原程式碼：計算邊界框、平滑、製作馬賽克效果 - 完全保留)
                        # ----------------------------------------------------
                        # 計算馬賽克區域
                        pts = np.array(finger_points, dtype=np.int32)
                        try:
                            hull = cv2.convexHull(pts)
                            x, y, w_box, h_box = cv2.boundingRect(hull)
                        except Exception:
                            x_min = min(fx)
                            x_max = max(fx)
                            y_min = min(fy)
                            y_max = max(fy)
                            x, y, w_box, h_box = x_min, y_min, x_max - x_min, y_max - y_min

                        pad = int(max(w_box, h_box) * BBOX_PADDING_RATIO) + BBOX_EXTRA_PADDING
                        x_min = x - pad
                        y_min = y - pad
                        x_max = x + w_box + pad
                        y_max = y + h_box + pad

                        if (x_max - x_min) < BBOX_MIN_DIMENSION:
                            cx = (x_min + x_max) // 2
                            x_min = cx - BBOX_MIN_DIMENSION // 2
                            x_max = cx + BBOX_MIN_DIMENSION // 2
                        if (y_max - y_min) < BBOX_MIN_DIMENSION:
                            cy = (y_min + y_max) // 2
                            y_min = cy - BBOX_MIN_DIMENSION // 2
                            y_max = cy + BBOX_MIN_DIMENSION // 2

                        if x_max > w: x_max = w
                        if y_max > h: y_max = h
                        if x_min < 0: x_min = 0
                        if y_min < 0: y_min = 0

                        if prev_bbox is not None:
                            px1, py1, px2, py2 = prev_bbox
                            x_min = int(px1 * alpha + x_min * (1 - alpha))
                            y_min = int(py1 * alpha + y_min * (1 - alpha))
                            x_max = int(px2 * alpha + x_max * (1 - alpha))
                            y_max = int(py2 * alpha + y_max * (1 - alpha))

                        prev_bbox = (x_min, y_min, x_max, y_max)

                        # 製作馬賽克效果
                        if x_max > x_min and y_max > y_min:
                            mosaic_w = x_max - x_min
                            mosaic_h = y_max - y_min
                            mosaic = img[y_min:y_max, x_min:x_max]
                            down_w = max(MOSAIC_DOWN_SAMPLE_MIN, 
                                       min(MOSAIC_DOWN_SAMPLE_MAX, 
                                           mosaic_w // MOSAIC_DOWN_SAMPLE_DIVISOR))
                            down_h = max(MOSAIC_DOWN_SAMPLE_MIN, 
                                       min(MOSAIC_DOWN_SAMPLE_MAX, 
                                           mosaic_h // MOSAIC_DOWN_SAMPLE_DIVISOR))
                            try:
                                mosaic = cv2.resize(mosaic, (down_w, down_h), 
                                                  interpolation=cv2.INTER_LINEAR)
                                mosaic = cv2.resize(mosaic, (mosaic_w, mosaic_h), 
                                                  interpolation=cv2.INTER_NEAREST)
                                img[y_min:y_max, x_min:x_max] = mosaic
                            except Exception:
                                pass

                        # 顯示警告文字
                        txt = WARNING_TEXT
                        tx = x_min
                        ty = y_min - 10
                        (tw, th), _ = cv2.getTextSize(txt, fontFace, WARNING_FONT_SCALE, WARNING_THICKNESS)
                        box_x1 = max(0, tx - WARNING_BG_PADDING)
                        box_y1 = max(0, ty - th - WARNING_BG_PADDING)
                        box_x2 = min(w, tx + tw + WARNING_BG_PADDING)
                        box_y2 = min(h, ty + WARNING_BG_PADDING)
                        cv2.rectangle(img, (box_x1, box_y1), (box_x2, box_y2), WARNING_BG_COLOR, -1)
                        cv2.putText(img, txt, (tx, ty), fontFace, WARNING_FONT_SCALE, WARNING_COLOR, WARNING_THICKNESS, lineType)
                    else:
                        if text:
                            cv2.putText(img, text, TEXT_POSITION, fontFace, 
                                      TEXT_FONT_SCALE, TEXT_COLOR, TEXT_THICKNESS, lineType)

            # --- 臉部馬賽克與追蹤邏輯 (替換原有 Haar Cascade 邏輯) ---
            
            # 判斷是否需要啟用臉部馬賽克
            # 移除原程式碼中對 face_cascade 的檢查
            if tracker.is_face_mosaic_enabled(): 
                
                # 1. 如果正在追蹤，執行追蹤器更新
                if tracking:
                    success, box = face_tracker.update(img)
                    if success:
                        x, y, w_box, h_box = [int(v) for v in box]
                        
                        if bbox_fixed:
                            mask_x_init, mask_y_init, mask_w, mask_h = bbox_fixed
                            center_x = x + w_box // 2
                            center_y = y + h_box // 2
                            
                            top_left_x = max(0, center_x - mask_w // 2)
                            top_left_y = max(0, center_y - mask_h // 2)
                            bottom_right_x = min(w, top_left_x + mask_w)
                            bottom_right_y = min(h, top_left_y + mask_h)
    
                            apply_mosaic(img, top_left_x, top_left_y, bottom_right_x, bottom_right_y, FACE_MOSAIC_LEVEL)
                            mask_timer = mask_duration
                        else:
                             tracking = False
                    else:
                        tracking = False
                        
                # 2. 如果追蹤失敗，但保留時間未到，繼續使用上次位置馬賽克
                elif mask_timer > 0 and bbox_fixed:
                    mask_x, mask_y, mask_w, mask_h = bbox_fixed
                    
                    top_left_x = mask_x
                    top_left_y = mask_y
                    bottom_right_x = mask_x + mask_w
                    bottom_right_y = mask_y + mask_h
                    
                    apply_mosaic(img, top_left_x, top_left_y, bottom_right_x, bottom_right_y, FACE_MOSAIC_LEVEL)
                    mask_timer -= 1
                    
                # 3. 如果追蹤未啟用且保留時間歸零，嘗試初始化追蹤器（偵測臉部）
                if not tracking and mask_timer <= 0:
                    face_results = face_mesh.process(img_rgb)
                    if face_results.multi_face_landmarks:
                        landmarks = face_results.multi_face_landmarks[0].landmark
                        xs = [int(lm.x * w) for lm in landmarks]
                        ys = [int(lm.y * h) for lm in landmarks]

                        expand = 40
                        x1 = max(0, min(xs) - expand)
                        y1 = max(0, min(ys) - expand)
                        x2 = min(w, max(xs) + expand)
                        y2 = min(h, max(ys) + expand)
                        
                        current_bbox = (x1, y1, x2 - x1, y2 - y1)
                        bbox_fixed = current_bbox 

                        try:
                            face_tracker = cv2.legacy.TrackerCSRT_create()
                            face_tracker.init(img, current_bbox)
                            tracking = True
                            mask_timer = mask_duration
                        except Exception as e:
                            print(f"CSRT 追蹤器初始化失敗: {e}")
                            tracking = False
                
                # 繪製臉部馬賽克警告文字
                if tracking or mask_timer > 0:
                    warning_txt = FACE_MOSAIC_WARNING_TEXT
                    
                    if bbox_fixed:
                        txt_x = bbox_fixed[0]
                        txt_y = bbox_fixed[1] - 10
                        
                        (tw, th), _ = cv2.getTextSize(
                            warning_txt, fontFace, 
                            FACE_MOSAIC_WARNING_FONT_SCALE, 
                            FACE_MOSAIC_WARNING_THICKNESS
                        )
                        cv2.rectangle(
                            img, 
                            (max(0, txt_x - 5), max(0, txt_y - th - 5)),
                            (min(w, txt_x + tw + 5), min(h, txt_y + 5)),
                            (0, 0, 0), 
                            -1
                        )
                        cv2.putText(
                            img, warning_txt, (txt_x, txt_y), 
                            fontFace, FACE_MOSAIC_WARNING_FONT_SCALE,
                            FACE_MOSAIC_WARNING_COLOR, 
                            FACE_MOSAIC_WARNING_THICKNESS, 
                            lineType
                        )
                    
            # --- 畫面資訊顯示與退出 (保持不變) ---
            
            stats = tracker.get_statistics()
            info_text = f"Bad Gestures: {stats['bad_gesture_count']}/{BAD_GESTURE_THRESHOLD}"
            cv2.putText(img, info_text, (10, 30), fontFace, 0.7, (255, 255, 0), 2, lineType)
            
            if stats['face_mosaic_enabled']:
                status_text = "Status: FACE MOSAIC ON (Stable Tracking)"
                status_color = (0, 0, 255)
            else:
                status_text = f"Status: Normal ({stats['remaining_warnings']} warnings left)"
                status_color = (0, 255, 0)
            cv2.putText(img, status_text, (10, 60), fontFace, 0.6, status_color, 2, lineType)
            
            cv2.imshow(WINDOW_NAME, img)

            if cv2.waitKey(5) == ord(EXIT_KEY):
                print("\n程式結束")
                print("重置計數器...")
                tracker.reset()
                break

    cap.release()
    cv2.destroyAllWindows()
    print("攝影機已關閉")
    print("感謝使用！")


if __name__ == "__main__":
    main()