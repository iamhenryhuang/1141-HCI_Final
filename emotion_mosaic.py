"""mix.py

Combine emotion detection and face mosaic: if the detected emotion is 'angry' or 'disgust',
pixelate (mosaic) the face region. Uses helper functions from `emotion.py` for font/text and
DeepFace analysis.
"""
import time
from collections import deque
import cv2
import numpy as np

try:
    from emotion import find_chinese_font, draw_text_pil, analyze_emotion, EMO_MAP
except Exception:
    # fallback: if emotion.py is missing or cannot be imported, provide minimal replacements
    def find_chinese_font():
        return None

    def draw_text_pil(img, text, pos=(10, 10), font_path=None, font_size=28, bg=(0, 0, 0, 160)):
        try:
            cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, font_size/30.0, (255,255,255), 2)
        except Exception:
            pass
        return img

    def analyze_emotion(face_bgr):
        return None

    EMO_MAP = {}


MOSAIC_LEVEL = 15
SMOOTH_WINDOW = 7
ANALYZE_EVERY = 3  # run DeepFace every N frames to save CPU


def mosaic_region(img, x, y, w, h, level=MOSAIC_LEVEL):
    if w <= 0 or h <= 0:
        return img
    roi = img[y:y+h, x:x+w]
    try:
        mh = max(1, int(h / level))
        mw = max(1, int(w / level))
        small = cv2.resize(roi, (mw, mh), interpolation=cv2.INTER_LINEAR)
        mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        img[y:y+h, x:x+w] = mosaic
    except Exception:
        pass
    return img


def main():
    font_path = find_chinese_font()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Cannot open webcam')
        return

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if cascade.empty():
        print('Failed to load face cascade from OpenCV installation.')
        cap.release()
        return

    smooth_buf = deque(maxlen=SMOOTH_WINDOW)
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        dominant_label = None
        dominant_prob = 0.0

        if len(faces) > 0:
            # choose largest face
            faces = sorted(faces, key=lambda r: r[2]*r[3], reverse=True)
            x, y, w, h = faces[0]
            pad = int(0.15 * max(w, h))
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(frame.shape[1], x + w + pad)
            y2 = min(frame.shape[0], y + h + pad)
            face_crop = frame[y1:y2, x1:x2].copy()

            # Run analysis only every N frames
            if frame_idx % ANALYZE_EVERY == 0:
                emos = analyze_emotion(face_crop)
                if emos:
                    smooth_buf.append(emos)

            # aggregate smoothing window
            if len(smooth_buf) > 0:
                agg = {}
                for d in smooth_buf:
                    for k, v in d.items():
                        agg[k] = agg.get(k, 0.0) + float(v)
                for k in agg:
                    agg[k] = agg[k] / len(smooth_buf)
                # dominant
                best = max(agg.items(), key=lambda kv: kv[1])
                dominant_label = best[0]
                dominant_prob = best[1]

            # If angry or disgust, mosaic the face region
            if dominant_label in ('angry', 'disgust'):
                display = mosaic_region(display, x1, y1, x2 - x1, y2 - y1, level=MOSAIC_LEVEL)

            # Draw rectangle for debugging (optional)
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # draw label
            if dominant_label:
                label_cn = EMO_MAP.get(dominant_label, dominant_label)
                text = f'{label_cn} {dominant_prob:.0f}%'
                display = draw_text_pil(display, text, pos=(x1, max(5, y1-35)), font_path=font_path, font_size=26)

        # show
        cv2.imshow('mix - angry -> mosaic (q to quit)', display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
