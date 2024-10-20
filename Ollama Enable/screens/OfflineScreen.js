import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Speech from 'expo-speech';

export default function ObjectDetectionScreen() {
  const [image, setImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const captureImage = async () => {
    let permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert('Permission to access camera is required!');
      return;
    }
    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });
    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const processImage = async () => {
    if (!image) {
      Alert.alert('Please capture an image before processing.');
      return;
    }

    setIsProcessing(true);
    let uriParts = image.split('.');
    let fileType = uriParts[uriParts.length - 1];

    const formData = new FormData();
    formData.append('image', {
      uri: image,
      type: `image/${fileType}`,
      name: `image.${fileType}`,
    });

    try {
      const response = await fetch('http://192.168.136.185:5000/detect_objects', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.ok) {
        const result = await response.json();
        const detectionText = result.summary || "No objects detected.";
        Speech.speak(detectionText); // Speak the detected text
        Alert.alert('Detection Result', detectionText);
      } else {
        throw new Error('Failed to process the image');
      }
    } catch (error) {
      console.error('Error processing image:', error);
      Alert.alert('Error', 'Failed to process the image. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Object Detection</Text>
      
      <View style={styles.imageContainer}>
        {image ? (
          <Image source={{ uri: image }} style={styles.image} />
        ) : (
          <TouchableOpacity style={styles.imagePlaceholder} onPress={captureImage}>
            <Ionicons name="camera" size={40} color="#fff" />
            <Text style={styles.imagePlaceholderText}>Capture Image</Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity
        style={[styles.button, isProcessing && styles.disabledButton]}
        onPress={processImage}
        disabled={isProcessing}
      >
        <Ionicons name="cloud-upload" size={24} color="#fff" />
        <Text style={styles.buttonText}>
          {isProcessing ? 'Processing...' : 'Process Image'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  imageContainer: {
    width: 200,
    height: 200,
    borderRadius: 10,
    overflow: 'hidden',
    marginBottom: 20,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imagePlaceholder: {
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0,0,0,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imagePlaceholderText: {
    color: '#000',
    marginTop: 10,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#4caf50',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 10,
  },
  disabledButton: {
    opacity: 0.5,
  },
});
