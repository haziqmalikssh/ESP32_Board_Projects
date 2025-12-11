import cv2

# --- Correct stream URL for your ESP32-CAM sketch ---
STREAM_URL = "http://192.168.1.30:81/stream"

print("Connecting to ESP32-CAM stream...")

cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    raise Exception("❌ ERROR: Cannot open ESP32 stream. Check URL and WiFi.")

print("✅ Connected to ESP32 stream!")

# Load OpenCV's built-in face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
                                     "haarcascade_frontalface_default.xml")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠ Frame read failed — reconnecting...")
        cap = cv2.VideoCapture(STREAM_URL)
        continue

    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    # Draw rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display video
    cv2.imshow("ESP32-CAM Face Detection", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

