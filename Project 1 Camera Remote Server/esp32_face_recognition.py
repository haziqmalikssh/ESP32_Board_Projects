import cv2
import dlib
import numpy as np
import os
import threading
import time
import mss
from flask import Flask, Response

# --- Manual Paths to Models ---
# ⚠️ VERIFY THIS PATH IS CORRECT ⚠️
MODELS_PATH = r"C:\Users\n\AppData\Local\Programs\Python\Python312\Lib\site-packages\face_recognition\models"

# --- Global Frame & Lock ---
processed_frame = None
frame_lock = threading.Lock()

# --- Load Face Recognition Models ---
try:
    print("Loading facial recognition models...")
    face_detector = dlib.get_frontal_face_detector()
    shape_predictor_path = os.path.join(MODELS_PATH, "shape_predictor_5_face_landmarks.dat")
    face_encoder_path = os.path.join(MODELS_PATH, "dlib_face_recognition_resnet_model_v1.dat")

    if not os.path.isfile(shape_predictor_path) or not os.path.isfile(face_encoder_path):
         raise FileNotFoundError("One or more dlib model files not found.")

    shape_predictor = dlib.shape_predictor(shape_predictor_path)
    face_encoder = dlib.face_recognition_model_v1(face_encoder_path)
    print("Facial recognition models loaded successfully.")

except Exception as e:
    print(f"Error loading dlib models: {e}")
    exit()

print("Setup complete. Starting screen capture processor.")


def get_face_encodings(input_frame):
    """
    Finds faces, returns encodings and locations. 
    Accepts an RGB frame (3-channel).
    """
    # 1. Resize for faster processing (downscale by 4)
    small_frame = cv2.resize(input_frame, (0, 0), fx=0.25, fy=0.25)
    
    # 2. Detect faces using the full RGB frame (bypassing grayscale conversion)
    face_locations = face_detector(small_frame, 0) 
    
    encodings = []
    for face in face_locations:
        landmarks = shape_predictor(small_frame, face)
        encoding = np.array(face_encoder.compute_face_descriptor(small_frame, landmarks))
        encodings.append(encoding)
            
    return encodings, face_locations


def stream_processor():
    """ CAPTURES VIDEO FROM SCREEN AND PERFORMS FACE RECOGNITION. """
    global processed_frame
    
    # Capture region is set to (0, 0) assuming you applied the HTML fix
    monitor = {"top": 0, "left": 0, "width": 640, "height": 480}
    
    try:
        with mss.mss() as sct:
            print(f"Screen Capture processor started. Capturing region: {monitor}")
            frame_counter = 0
            while True:
                start_time = time.time() # Start time for performance logging
                frame_counter += 1
                
                # 1. Get raw pixels from the screen
                sct_img = sct.grab(monitor)
                
                # 2. Convert to a NumPy array (OpenCV format) and force dtype
                frame = np.array(sct_img).astype(np.uint8)

                # 3. Explicitly convert the 4-channel BGRA screen capture to 3-channel BGR
                if frame.shape[2] == 4:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # 4. Convert the BGR frame to RGB for dlib/face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # --- LOGGING STEP 1: Processing start ---
                print(f"Frame {frame_counter}: Capture OK. Starting face recognition...") 
                
                # Get face encodings and locations - PASS THE RGB FRAME
                _, face_locations = get_face_encodings(rgb_frame)

                # --- NEW FEEDBACK LOGIC ---
                feedback_text = ""
                # Check if any faces were detected
                if len(face_locations) > 0:
                    feedback_text = f"Faces detected: {len(face_locations)}"
                    print(f"✅ Faces detected! Found {len(face_locations)}.") # Console message
                else:
                    feedback_text = "No faces detected"
                    print(f"❌ No faces detected.") # Console message

                # --- Draw feedback text on the frame ---
                cv2.putText(
                    frame, feedback_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA
                )
                
                # Draw rectangles on the final BGR frame 
                for face_location in face_locations:
                    top, right, bottom, left = (face_location.top() * 4), (face_location.right() * 4), (face_location.bottom() * 4), (face_location.left() * 4)
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # --- LOGGING STEP 2: Lock release and loop end ---
                with frame_lock:
                    processed_frame = frame.copy()
                
                total_time = time.time() - start_time
                print(f"Frame {frame_counter}: Processing complete. Total time: {total_time:.4f}s")
                
                # Adjust sleep time based on performance
                if total_time < 0.033:
                    time.sleep(0.033 - total_time) 

    except Exception as e:
        print(f"An unexpected error occurred in the processor thread: {e}")
        raise 
    
    print("Screen Capture processor finished.")


# --- Flask Server Setup (Remains the same) ---

app = Flask(__name__)

def generate_frames():
    """ Generator function to create the MJPEG stream for the browser. """
    global processed_frame
    while True:
        with frame_lock:
            if processed_frame is None:
                time.sleep(0.1)
                continue
            
            (flag, encodedImage) = cv2.imencode(".jpg", processed_frame)
            if not flag:
                continue
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\r' + bytearray(encodedImage) + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """ Route to serve the processed MJPEG stream. """
    return Response(generate_frames(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/')
def index():
    """ Route to display the video feed in a browser with a light background. """
    server_ip = app.config['SERVER_NAME'].split(':')[0] if ':' in app.config.get('SERVER_NAME', '127.0.0.1:5000') else app.config.get('SERVER_NAME', '127.0.0.1')
    
    return f"""
    <html>
        <head>
            <title>Face Recognition Stream</title>
            <style>
                body {{ 
                    background: #f0f0f0; 
                    color: #333; 
                    font-family: sans-serif; 
                    text-align: center; 
                }}
                h1 {{ color: #007bff; }}
                img {{ 
                    border: 3px solid #555; 
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
                }}
            </style>
        </head>
        <body>
            <h1>Processed Video Stream (Face Recognition)</h1>
            <img src='http://{server_ip}:5000/video_feed' width='640'>
            <p>Stream powered by your Python script on {server_ip}:5000</p>
        </body>
    </html>
    """

def main():
    processor_thread = threading.Thread(target=stream_processor)
    processor_thread.daemon = True 
    processor_thread.start()

    print("\n---------------------------------------------------------")
    print("Ready! Access the processed stream via a browser at:")
    print("    http://<Your_PC_IP_Address>:5000/")
    print("---------------------------------------------------------")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nServer shutting down.")

if __name__ == "__main__":
    main()