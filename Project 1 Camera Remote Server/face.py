import cv2
import numpy as np
import mss
import time

# ---- Configuration ----
# Screen capture area (adjust these values to match your browser window)
region = {
    "top": 175,
    "left": 640,
    "width": 640,
    "height": 480
}

# Face detection parameters
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5
MIN_SIZE = (30, 30)

# Performance settings
TARGET_FPS = 30
FRAME_DELAY = int(1000 / TARGET_FPS)  # milliseconds

# Display settings
SHOW_FPS = True
TEXT_COLOR = (0, 255, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX

def main():
    # Load Haar cascade
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    if face_cascade.empty():
        print("Error: Could not load Haar cascade classifier")
        return
    
    print("Face Detection Started")
    print(f"Capturing region: {region}")
    print("Press 'q' to quit, 's' to save screenshot, 'r' to reset region")
    
    frame_count = 0
    start_time = time.time()
    fps = 0
    
    with mss.mss() as sct:
        while True:
            loop_start = time.time()
            
            # Capture screen
            try:
                screenshot = sct.grab(region)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            except Exception as e:
                print(f"Error capturing screen: {e}")
                break
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=SCALE_FACTOR,
                minNeighbors=MIN_NEIGHBORS,
                minSize=MIN_SIZE,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            
            # Calculate and display FPS
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()
            
            if SHOW_FPS:
                fps_text = f"FPS: {fps:.1f} | Faces: {len(faces)}"
                cv2.putText(
                    frame,
                    fps_text,
                    (10, 30),
                    FONT,
                    0.7,
                    TEXT_COLOR,
                    2
                )
            
            # Display the frame
            cv2.imshow("Face Detection (ESP32 via Screen Capture)", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('s'):
                filename = f"face_detection_{int(time.time())}.png"
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved: {filename}")
            elif key == ord('r'):
                print("Region reset - adjust window and restart")
            
            # Throttle to target FPS
            loop_time = (time.time() - loop_start) * 1000
            if loop_time < FRAME_DELAY:
                time.sleep((FRAME_DELAY - loop_time) / 1000)
    
    cv2.destroyAllWindows()
    print("Face detection stopped")

if __name__ == "__main__":
    main()