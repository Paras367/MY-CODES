import cv2

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.resize(frame, (256, 256))

    # Cartoon Effect 1
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 9)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 10)
    color = cv2.bilateralFilter(image, 12, 250, 250)
    cartoon_cartoonize = cv2.bitwise_and(color, color, mask=edges)

    # Cartoon Effect 2
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayImage = cv2.GaussianBlur(grayImage, (9, 9), 0)
    edgeImage = cv2.Laplacian(grayImage, -1, ksize=5)
    edgeImage = 255 - edgeImage
    ret, edgeImage = cv2.threshold(edgeImage, 150, 255, cv2.THRESH_BINARY)
    edgePreservingImage = cv2.edgePreservingFilter(image, flags=2, sigma_s=50, sigma_r=0.4)
    cartoon_blurring = cv2.bitwise_and(edgePreservingImage, edgePreservingImage, mask=edgeImage)

    # Cartoon Stylization
    cartoon_stylization = cv2.stylization(image, sigma_s=150, sigma_r=0.25)

    # Pencil Sketch
    cartoon_pencil_bw, cartoon_pencil = cv2.pencilSketch(image, sigma_s=10, sigma_r=0.5, shade_factor=0.01)

    # Display outputs
    cv2.imshow("Stylization", cartoon_stylization)
    cv2.imshow("Pencil Sketch", cartoon_pencil)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
