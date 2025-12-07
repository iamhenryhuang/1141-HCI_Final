"""
手勢識別主程式
使用 MediaPipe 和 OpenCV 進行即時手勢識別，並對不雅手勢進行馬賽克處理
"""

import cv2
import mediapipe as mp
from gesture_tracker import GestureTracker
from gesture_recognizer import GestureRecognizer
from visualizer import Visualizer
from face_detector import FaceDetector
from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    MODEL_COMPLEXITY, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE,
    BLACKLIST_GESTURES, DEBOUNCE_FRAMES,
    BAD_GESTURE_THRESHOLD, GESTURE_LOG_FILE,
    EXIT_KEY
)

class GestureRecognitionApp:
    def __init__(self):
        """初始化應用程式"""
        # 1. 初始化各個模組
        self.tracker = GestureTracker(data_file=GESTURE_LOG_FILE)
        self.tracker.threshold = BAD_GESTURE_THRESHOLD
        
        self.recognizer = GestureRecognizer()
        self.visualizer = Visualizer()
        self.face_detector = FaceDetector()
        
        # 2. 初始化 MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=MODEL_COMPLEXITY,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        
        # 3. 初始化攝影機
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        
        # 4. 狀態變數
        self.gesture_buffer_text = ''
        self.gesture_buffer_count = 0
        self.current_gesture_logged = False
        
        self.print_startup_info()

    def print_startup_info(self):
        """顯示啟動資訊"""
        stats = self.tracker.get_statistics()
        print("=" * 50)
        print("手勢識別系統啟動中...")
        print(f"攝影機: {CAMERA_INDEX}")
        print(f"解析度: {FRAME_WIDTH} x {FRAME_HEIGHT}")
        print(f"今日不雅手勢次數: {stats['bad_gesture_count']}")
        print(f"按 '{EXIT_KEY}' 鍵退出程式")
        print("=" * 50)

    def process_frame(self, img):
        """處理單一影格"""
        h, w, _ = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        # -----------------------------------------------------
        # 手部偵測與識別
        # -----------------------------------------------------
        if results.multi_hand_landmarks:
            detections = []
            
            for hand_landmarks in results.multi_hand_landmarks:
                # 繪製骨架
                self.visualizer.draw_landmarks(img, hand_landmarks)
                
                # 轉換座標格式
                landmarks = []
                fx, fy = [], []
                for lm in hand_landmarks.landmark:
                    x_px, y_px = int(lm.x * w), int(lm.y * h)
                    landmarks.append((x_px, y_px))
                    fx.append(x_px)
                    fy.append(y_px)
                
                # 識別手勢
                gesture_name = self.recognizer.recognize(landmarks)
                
                detections.append({
                    'text': gesture_name,
                    'landmarks': landmarks,
                    'fx': fx,
                    'fy': fy
                })

            # -----------------------------------------------------
            # 判斷是否觸發不雅手勢計數 (Debounce Logic)
            # -----------------------------------------------------
            self.update_gesture_status(detections)

            # -----------------------------------------------------
            # 繪製結果 (文字或馬賽克)
            # -----------------------------------------------------
            for d in detections:
                text = d['text']
                
                # 判斷是否需要馬賽克
                should_mosaic = (text in BLACKLIST_GESTURES and 
                               text == self.gesture_buffer_text and 
                               self.gesture_buffer_count >= DEBOUNCE_FRAMES)
                
                if should_mosaic:
                    self.visualizer.apply_hand_mosaic(img, d['landmarks'], d['fx'], d['fy'], w, h)
                else:
                    self.visualizer.draw_gesture_text(img, text)

        # -----------------------------------------------------
        # 臉部馬賽克處理 (若已達閾值)
        # -----------------------------------------------------
        if self.tracker.is_face_mosaic_enabled():
            faces = self.face_detector.detect(img)
            self.visualizer.draw_face_mosaic(img, faces)

        # -----------------------------------------------------
        # 顯示統計資訊
        # -----------------------------------------------------
        self.visualizer.draw_stats(img, self.tracker.get_statistics(), BAD_GESTURE_THRESHOLD)
        
        return img

    def update_gesture_status(self, detections):
        """更新手勢狀態與計數"""
        frame_candidates = [d['text'] for d in detections if d['text'] in BLACKLIST_GESTURES]
        
        if frame_candidates:
            candidate = max(set(frame_candidates), key=frame_candidates.count)
            if candidate == self.gesture_buffer_text:
                self.gesture_buffer_count += 1
                if self.gesture_buffer_count >= DEBOUNCE_FRAMES and not self.current_gesture_logged:
                    self.tracker.add_bad_gesture(candidate)
                    self.current_gesture_logged = True
            else:
                self.gesture_buffer_text = candidate
                self.gesture_buffer_count = 1
                self.current_gesture_logged = False
        else:
            self.gesture_buffer_text = ''
            self.gesture_buffer_count = 0
            self.current_gesture_logged = False

    def run(self):
        """啟動主迴圈"""
        if not self.cap.isOpened():
            print("錯誤：無法開啟攝影機")
            return

        print("系統運行中...")
        
        try:
            while True:
                ret, img = self.cap.read()
                if not ret:
                    break
                    
                img = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))
                
                # 處理畫面
                img = self.process_frame(img)
                
                # 顯示畫面
                cv2.imshow('Hand Gesture Recognition', img)

                if cv2.waitKey(5) == ord(EXIT_KEY):
                    print("\n程式結束")
                    self.tracker.reset()
                    break
        finally:
            self.cleanup()

    def cleanup(self):
        """清理資源"""
        self.cap.release()
        self.hands.close()
        cv2.destroyAllWindows()
        print("攝影機已關閉")

def main():
    app = GestureRecognitionApp()
    app.run()

if __name__ == "__main__":
    main()