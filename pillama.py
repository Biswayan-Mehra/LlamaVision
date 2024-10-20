import cv2
import torch
from ultralytics import YOLO
from flask import Flask, request, jsonify
import requests
import json
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load the YOLO model
model = YOLO("yolov8n.pt")  # You can replace this with any YOLOv8 model version
class_names = model.names

# Function to generate the natural language summary using the LLaMA model
def generate_text(prompt):
    system_prompt = '''You are an assistant that summarizes YOLO object detection results. 
    Given a detection string, create a natural language summary. 
    Use "There is/are" to start the sentence. 
    Combine multiple detections of the same object.
    Use "and" to connect different object types.
    Keep the summary concise and in a single sentence.'''

    full_prompt = f"{system_prompt}\n\nInput: {prompt}\nOutput:"
    
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": "llama3.2:1b",
        "prompt": full_prompt
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                response_data = json.loads(decoded_line)
                if 'response' in response_data:
                    result += response_data['response']
        return result.strip()
    else:
        return f"Error: {response.status_code}"


# Define position labels based on object coordinates
def get_position(x_center, frame_width):
    if x_center < frame_width / 3:
        return "left"
    elif x_center > (frame_width * 2 / 3):
        return "right"
    else:
        return "center"

# Route for object detection and summary generation
@app.route('/detect_objects', methods=['POST'])
def detect_objects():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Read the image from the request
    file = request.files['image']
    img_array = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    if frame is None:
        return jsonify({'error': 'Invalid image format'}), 400
    
    # Perform object detection
    results = model(frame)[0]

    # Initialize counters for detected objects and positions
    objects = {}

    # Get frame dimensions (width and height)
    frame_height, frame_width, _ = frame.shape

    # Iterate over the detected objects
    for det in results.boxes:
        class_id = int(det.cls)
        class_name = class_names[class_id]

        # Get bounding box coordinates (x1, y1, x2, y2)
        x1, y1, x2, y2 = det.xyxy[0]  # Assuming results.boxes returns [x1, y1, x2, y2]

        # Calculate the center of the bounding box
        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2

        # Get position based on the x_center
        position = get_position(x_center, frame_width)

        # Update the object count and position
        if class_name not in objects:
            objects[class_name] = {"count": 0, "positions": []}
        objects[class_name]["count"] += 1
        objects[class_name]["positions"].append(position)

    # Generate a textual summary of the detection
    total_msg = ""
    for obj, data in objects.items():
        msg = f"Detected {data['count']} {obj}(s) at positions: {data['positions']}"
        total_msg += msg + "\n"
    
    # Generate the natural language response
    response_text = generate_text(total_msg)

    # Return the detection summary and generated text
    return jsonify({'detections': total_msg, 'summary': response_text})


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
