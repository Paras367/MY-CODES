import cv2
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
video_capture = cv2.VideoCapture(0)

while True:
    check, frame = video_capture.read()
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = cascade.detectMultiScale(
        gray_image, scaleFactor=2.0, minNeighbors=4)

    for x, y, w, h in face:
        image = cv2.rectangle(frame, (x, y), (x+w, y+h), 
                              (0, 255, 0), 3)
        image[y:y+h, x:x+w] = cv2.medianBlur(image[y:y+h, x:x+w],
                                             35)
    cv2.imshow('face blurred', frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

# SoftwareLabs
# softwarelabs.lovable.app
# Made with Love by PARAS DHIMAN
# CODEWITHPARAS
