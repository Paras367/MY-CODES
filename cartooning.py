import cv2
import numpy as np

def cartoonify(image):
    # Step 1: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 2: Apply median blur
    gray_blur = cv2.medianBlur(gray, 7)

    # Step 3: Detect edges using adaptive threshold
    edges = cv2.adaptiveThreshold(gray_blur, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)

    # Step 4: Apply bilateral filter to smooth colors
    color = cv2.bilateralFilter(image, 9, 250, 250)

    # Step 5: Combine edges and color image
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    return cartoon

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for speed (optional)
    frame = cv2.resize(frame, (640, 480))

    # Apply cartoon effect
    cartoon_frame = cartoonify(frame)

    # Show the output
    cv2.imshow('Cartoon Live', cartoon_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
