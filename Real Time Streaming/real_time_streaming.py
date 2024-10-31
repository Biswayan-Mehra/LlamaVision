import cv2
import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import imagehash
import asyncio
import aiohttp
import time
import json
import sys
import threading

# Use GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load pre-trained ResNet model (for feature extraction)
model = resnet18(weights="IMAGENET1K_V1")
model = nn.Sequential(*list(model.children())[:-1])  # Remove last fully connected layer
model = model.to(device)
model.eval()

# Define the preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to the size expected by ResNet
    transforms.ToTensor(),
])

# Prompt list
prompts = [
    "I am giving you an image with 6 images side to side, give a short description in 2 lines. Don't mention it's an image.",
    "Can you find my <keyword>? Answer only in yes or not yet!",
    "Can you find the animal llama? Answer only in 'Yes! I found the Llama!' or in 'No, where are you Llama?!'",
    "End the program."  # This prompt will terminate the program
]

# Global variables for prompt and descriptions
current_prompt_index = 0
descriptions = []

# Function to get frame features
def get_frame_features(frame):
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    frame_preprocessed = preprocess(pil_image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = model(frame_preprocessed)
    return features.cpu()

# Cosine similarity for frame comparison
def is_different_cosine(features1, features2, threshold=0.9):
    similarity = cosine_similarity(features1.view(1, -1), features2.view(1, -1))[0][0]
    return similarity < threshold

# Perceptual hashing (pHash) for frame comparison
def get_phash(image):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    return imagehash.phash(pil_image)

def is_different_phash(hash1, hash2, hash_threshold=5):
    return hash1 - hash2 > hash_threshold

# Clear image check using Laplacian variance and edges
def is_clear_image(gray_frame, laplacian_threshold=300, edge_threshold=100):
    laplacian_var = cv2.Laplacian(gray_frame, cv2.CV_64F).var()
    if laplacian_var < laplacian_threshold:
        return False
    edges = cv2.Canny(gray_frame, 100, 200)
    return np.sum(edges > 0) > edge_threshold

# Motion detection using optical flow
def has_significant_motion(gray1, gray2, motion_threshold=0.05):
    if gray1.shape != gray2.shape:
        gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))

    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    return np.mean(magnitude) > motion_threshold

# Combined check for frame difference
def is_frame_significantly_different(features1, features2, hash1, hash2, cos_threshold=0.9, hash_threshold=5):
    return is_different_cosine(features1, features2, threshold=cos_threshold) or is_different_phash(hash1, hash2, hash_threshold)

# Function to get current timestamp with milliseconds
def get_timestamp():
    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + f"-{int(time.time() * 1000) % 1000:03d}"

# Save the combined frame and descriptions to JSON
def save_combined_image(image_list, folder, count):
    combined_image = np.hstack(image_list)

    # Use timestamp with milliseconds in filename
    timestamp = get_timestamp()
    filename = os.path.join(folder, f"combined_frame_{timestamp}.jpg")

    cv2.imwrite(filename, combined_image)

    # Process the image asynchronously and save description
    asyncio.run(process_image_async(filename))

async def process_image_async(image_path):
    print("\nUploading image... Please wait.")
    sys.stdout.flush()

    image_url = await upload_image_async(image_path)
    asyncio.create_task(show_processing_progress())

    result = await process_image_api(image_url)

    # Save description, filename, and timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    descriptions.append({"filename": image_path, "description": result, "timestamp": timestamp})
    with open('descriptions.json', 'w') as json_file:
        json.dump(descriptions, json_file, indent=4)

    print(f"\nDESCRIPTION: {result}\n")

async def show_processing_progress():
    for i in range(4):
        await asyncio.sleep(1)
        print("Processing...", "." * (i + 1), end='\r')
        sys.stdout.flush()

async def upload_image_async(image_path):
    url = 'https://0x0.st'
    async with aiohttp.ClientSession() as session:
        with open(image_path, 'rb') as file:
            async with session.post(url, data={'file': file}) as response:
                return await response.text()

async def process_image_api(image_url):
    global current_prompt_index
    api_url = "https://proxy.tune.app/chat/completions"
    headers = {
        "Authorization": "sk-tune-XJBlBdjj0Mh437ZSmy2OStKFGh9OQ0OD5JN",
        "Content-Type": "application/json",
    }
    data = {
        "temperature": 0.8,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompts[current_prompt_index]}, {"type": "image_url", "image_url": {"url": image_url}}]}
        ],
        "model": "meta/llama-3.2-90b-vision",
        "frequency_penalty": 0,
        "max_tokens": 900
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=data) as response:
            result = await response.json()
            return result['choices'][0]['message']['content']

# Function to replace keyword in the first prompt
def replace_keyword_in_prompt():
    keyword = input("Enter the keyword to replace in prompt 2: ")  # Prompt for user input
    prompts[1] = f"Can you find my {keyword}? Answer only in yes or not yet!"  # Update the prompt
    print(f"Updated prompt: {prompts[1]}")  # Print updated prompt to console

# Thread function to handle keyword replacement
def handle_keyword_replacement():
    keyword_thread = threading.Thread(target=replace_keyword_in_prompt)
    keyword_thread.start()  # Start the thread, making it non-blocking

def main():
    global current_prompt_index

    save_folder = 'captured_frames'
    os.makedirs(save_folder, exist_ok=True)

    video_url = 'http://192.168.169.144:8080/video'  # Replace with actual video stream URL
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print("Error: Couldn't open video stream.")
        return

    count = 0
    last_frame = None
    frame_skip = 10
    frame_counter = 0
    image_buffer = []

    features_last = None
    phash_last = None

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Failed to grab frame. Attempting to reconnect...")
            cap.release()
            cap = cv2.VideoCapture(video_url)  # Try to reconnect
            continue

        frame_counter += 1
        if frame_counter % frame_skip != 0:
            continue

        gray_frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (640, 360))
        frame_resized = cv2.resize(frame, (640, 360))

        if not is_clear_image(gray_frame):
            print(f"Skipping frame {frame_counter} due to blurriness.")
            continue

        if last_frame is not None:
            gray_last_frame = cv2.resize(cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY), (640, 360))
            if not has_significant_motion(gray_last_frame, gray_frame):
                print(f"Skipping frame {frame_counter} due to minor motion.")
                continue

        features_current = get_frame_features(frame_resized)
        phash_current = get_phash(frame_resized)

        if last_frame is None or is_frame_significantly_different(features_current, features_last, phash_current, phash_last):
            image_buffer.append(frame_resized)
            features_last = features_current
            phash_last = phash_current
            last_frame = frame_resized

        if len(image_buffer) == 6:
            save_combined_image(image_buffer, save_folder, count)
            image_buffer = []
            count += 1

        cv2.imshow('Video Stream', cv2.resize(frame, (700, 400)))

        # Check for numeric key presses
        key = cv2.waitKey(1) & 0xFF

        if key == ord('0'):  # Press '0' to exit
            print("Exiting program.")
            break
        elif ord('1') <= key <= ord('9'):  # Press 1-9 to change the prompt
            prompt_num = key - ord('1')  # Convert key press to index (0-based)
            if prompt_num < len(prompts):
                current_prompt_index = prompt_num
                print(f"Switching to prompt {current_prompt_index + 1}: {prompts[current_prompt_index]}")

                # Check if the user selected prompt index 1 (for replacing keyword)
                if current_prompt_index == 1:
                    handle_keyword_replacement()  # Start a non-blocking thread for keyword replacement

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
