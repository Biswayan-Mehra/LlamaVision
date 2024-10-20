# Assistive Technology for the Visually Impaired Using LLama 3

This project aims to empower individuals with visual impairments through advanced AI technology powered by LLama 3. It consists of three core components: **Ollama Understand**, **Ollama Enable**, and **piLlama**. Together, they enhance accessibility through natural language understanding, device integration, and real-time streaming.

## Features

### 1. Ollama Understand

Ollama Understand is a multimodal understanding system designed to assist visually impaired users in comprehending their environment through audio and visual inputs. Key features include:

- **Speech-to-Text Translation**: Converts spoken audio into text using the Sarvam AI Speech-to-Text API, supporting multiple languages.
- **Multimodal Object Understanding**: Utilizes LLama 3.2 (90B Vision) to analyze images and provide context-aware responses based on user prompts.
- **Audio Feedback**: Converts generated text responses into speech using OpenAI's text-to-speech models, providing a seamless interaction experience.
- **Language Translation**: Automatically translates responses into the user's language with the Sarvam AI Translation API before converting them to speech.
- **Dynamic Interaction**: Users can ask questions about images and receive natural language explanations, enriching the interactive experience.

### 2. Ollama Enable

**Ollama Enable** is a React Native mobile application that integrates all project features, making them accessible on mobile devices. It allows users to:

- Use voice commands to control devices and access information.
- Engage with the AI through a user-friendly mobile interface to navigate and read in real-world environments.
- Connect seamlessly to other components like **Ollama Understand**, **piLlama**, and real-time streaming for a comprehensive assistive experience.

### 3. piLlama using Raspberry Pi 4

**piLlama** combines YOLOv8 for object detection and LLama 3.2 (1B) for generating natural language descriptions, all running efficiently on a Raspberry Pi 4. Key features include:

- **YOLOv8 Object Detection**: Detects and localizes objects in images, identifying their positions within the frame.
- **Natural Language Summaries**: Generates concise descriptions of detected objects, conveying their count and positions in a single sentence.
- **Real-time Object Detection**: Fast and lightweight, suitable for the Raspberry Pi 4's limited computational power.
- **Position-based Descriptions**: Provides users with spatial awareness of detected objects (left, center, right).
- **Offline Capability**: Operates without internet access, ensuring reliable support in various environments.

### 4. Real-Time Streaming using LLama 3.2 (90B)

This component processes live video streams for advanced feature extraction, image recognition, and scene understanding in real-time. Key functionalities include:

- **Feature Extraction**: Utilizes ResNet-18 for image feature extraction, comparing frames using cosine similarity.
- **Blurriness Detection**: Identifies and skips blurry frames using Laplacian variance and edge detection.
- **Motion Detection**: Applies optical flow to detect significant motion, ignoring minor changes.
- **Image Multimodal Capabilities**: Combines image hashing and feature-based checks to identify significant frame differences.
- **Prompt-based Interaction**: Responds to pre-defined prompts for specific keywords or objects, providing brief descriptions.
- **Image Processing API Integration**: Asynchronously uploads processed frames to an external API for concise descriptions.
- **Real-time Feedback**: Delivers descriptive feedback in text form, helping users understand the video stream's contents.

### 5. Llama Long Video Analysis Project

An AI system using Llama 3.2 90B Vision model for analyzing long videos and answering questions about their content. The system processes YouTube videos by extracting and analyzing frame sequences.

Key Features
- YouTube video downloads via yt-dlp
- Frame extraction at customizable FPS
- Batch frame analysis
- Vision-based scene understanding
- Natural language Q&A capability
- Frame sequence visualization

Technical Stack
- Meta Llama 3.2 90B Vision Instruct model
- Google Cloud Platform
- Python with OpenCV
- Vertex AI integration
