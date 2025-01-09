from flask import Flask, request, jsonify
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_and_predict(image_path, model_path="ecg_classification_model.tflite"):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")

    # Preprocess the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("No contours found in image.")

    # Process largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    cropped_image = image[y : y + h, x : x + w]

    # Resize the image
    target_width, target_height = 960, 540
    resized_image = cv2.resize(
        cropped_image, (target_width, target_height), interpolation=cv2.INTER_CUBIC
    )

    # Preprocess for model
    image_array = img_to_array(resized_image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    # Load and use TFLite model
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]["index"], image_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]["index"])
    print(predictions)

    class_index = np.argmax(predictions[0])

    class_labels = [
        "Patient that have History of MI",
        "Patient that have Abnormal Heartbeat",
        "Normal Person ECG Image",
        "Myocardial Infarction Patient",
    ]

    return {
        "predicted_class": class_labels[class_index],
        "confidence": float(predictions[0][class_index]),
    }


@app.route("/")
def index():
    return "Hello World!"


@app.route("/predict", methods=["POST"])
def predict():
    # Check if image file is present in request
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Check if file is selected
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check file extension
    if not allowed_file(file.filename):
        return (
            jsonify({"error": "Invalid file type. Allowed types: png, jpg, jpeg"}),
            400,
        )

    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Process the image and get prediction
        result = preprocess_and_predict(filepath)

        # Clean up - remove uploaded file
        os.remove(filepath)

        return jsonify(result)

    except Exception as e:
        # Clean up in case of error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500


port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
