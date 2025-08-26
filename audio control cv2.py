import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Webcam
cap = cv2.VideoCapture(0)

# Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Audio setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    lm_list = []

    if result.multi_hand_landmarks:
        for hand_landmark in result.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmark.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((cx, cy))
            mp_draw.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

    # Only if landmarks exist
    if len(lm_list) >= 9:
        x1, y1 = lm_list[4]   # Thumb tip
        x2, y2 = lm_list[8]   # Index finger tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw
        cv2.circle(frame, (x1, y1), 8, (255, 0, 255), -1)
        cv2.circle(frame, (x2, y2), 8, (255, 0, 255), -1)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)
        cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

        # Calculate distance
        distance = math.hypot(x2 - x1, y2 - y1)

        # Convert distance to volume range
        vol = np.interp(distance, [20, 200], [min_vol, max_vol])
        volume.SetMasterVolumeLevel(vol, None)

        # Show volume percentage
        vol_percent = np.interp(distance, [20, 200], [0, 100])
        cv2.putText(frame, f'Volume: {int(vol_percent)}%', (40, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("Virtual Volume Control", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
