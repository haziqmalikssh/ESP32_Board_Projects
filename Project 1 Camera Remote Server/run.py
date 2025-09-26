import dlib
import os
import sys

# The path to the models folder.
# We are hardcoding this path to bypass any automatic path discovery issues.
models_path = r"C:\Users\n\AppData\Local\Programs\Python\Python312\Lib\site-packages\face_recognition\models"

# Check if the models folder exists
if not os.path.isdir(models_path):
    print(f"Error: The models directory does not exist at {models_path}")
    sys.exit(1)

# The full path to the face recognition model file
model_file = os.path.join(models_path, "dlib_face_recognition_resnet_model_v1.dat")

# Check if the model file exists
if not os.path.isfile(model_file):
    print(f"Error: The model file does not exist at {model_file}")
    sys.exit(1)

print("Attempting to load the model...")
try:
    # Use dlib to load the model directly
    face_encoder = dlib.face_recognition_model_v1(model_file)
    print("Success! The face recognition model was loaded correctly.")
    print("This confirms the file path is correct and the models are usable.")

except Exception as e:
    print(f"An error occurred while loading the model: {e}")
