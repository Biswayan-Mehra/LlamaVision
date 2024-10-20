import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Image, Alert, ScrollView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

export default function ProfileScreen({ navigation }) {
  const [image, setImage] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [audioUri, setAudioUri] = useState(null);
  const [recording, setRecording] = useState(null);
  const [responseAudio, setResponseAudio] = useState(null);
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
      uploadImage(result.assets[0].uri);
    }
  };

  const uploadImage = async (uri) => {
    const formData = new FormData();
    formData.append('file', {
      uri: uri,
      type: 'image/jpeg',
      name: 'image.jpg'
    });

    try {
      const response = await fetch('https://0x0.st', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const url = await response.text();
        setImageUrl(url.trim());
      } else {
        throw new Error('Image upload failed');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      Alert.alert('Error', 'Failed to upload image. Please try again.');
    }
  };

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission to access microphone is required!');
        return;
      }
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      const recording = new Audio.Recording();
      await recording.prepareToRecordAsync(Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY);
      await recording.startAsync();
      setRecording(recording);
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setAudioUri(uri);
      setRecording(null);
    } catch (error) {
      console.error('Failed to stop recording', error);
    }
  };

  const processData = async () => {
    if (!imageUrl || !audioUri) {
      Alert.alert('Please capture both image and audio before processing.');
      return;
    }

    setIsProcessing(true);
    const apiUrl = 'http://44.243.42.123:5000/process';
    const formData = new FormData();

    formData.append('audio', {
      uri: audioUri,
      type: 'audio/wav',
      name: 'audio.wav',
    });

    formData.append('img_url', imageUrl);
    formData.append('prompt', 'Answer the below question based on the given top right image in ONLY 60 WORDS OR LESS in a paragraph form only\n\n\n');

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();

      if (result.audio) {
        const audioPath = `${FileSystem.documentDirectory}response_audio.wav`;
        await FileSystem.writeAsStringAsync(audioPath, result.audio, {
          encoding: FileSystem.EncodingType.Base64,
        });
        setResponseAudio(audioPath);
        Alert.alert('Processing complete', 'Audio response saved.');
      }
    } catch (error) {
      console.error('Error processing data:', error);
      Alert.alert('Error', 'Failed to process data. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const playResponseAudio = async () => {
    if (responseAudio) {
      try {
        const { sound } = await Audio.Sound.createAsync({ uri: responseAudio });
        await sound.playAsync();
      } catch (error) {
        console.error('Error playing audio:', error);
        Alert.alert('Error', 'Failed to play audio. Please try again.');
      }
    } else {
      Alert.alert('No response audio available');
    }
  };

  return (
    <LinearGradient colors={['#4c669f', '#3b5998', '#192f6a']} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollView}>
        <Text style={styles.title}>Understanding Llamas</Text>
        
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
          style={[styles.button, recording && styles.recordingButton]}
          onPress={recording ? stopRecording : startRecording}
        >
          <Ionicons name={recording ? "stop" : "mic"} size={24} color="#fff" />
          <Text style={styles.buttonText}>
            {recording ? "Stop Recording" : "Start Recording"}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, (!imageUrl || !audioUri) && styles.disabledButton]}
          onPress={processData}
          disabled={!imageUrl || !audioUri || isProcessing}
        >
          <Ionicons name="cloud-upload" size={24} color="#fff" />
          <Text style={styles.buttonText}>
            {isProcessing ? "Processing..." : "Process Data"}
          </Text>
        </TouchableOpacity>

        {responseAudio && (
          <TouchableOpacity style={styles.button} onPress={playResponseAudio}>
            <Ionicons name="play" size={24} color="#fff" />
            <Text style={styles.buttonText}>Play Response</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity style={styles.homeButton} onPress={() => navigation.navigate('Home')}>
          <Ionicons name="home" size={24} color="#fff" />
          <Text style={styles.buttonText}>Go to Home</Text>
        </TouchableOpacity>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 30,
    textAlign: 'center',
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
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imagePlaceholderText: {
    color: '#fff',
    marginTop: 10,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    marginVertical: 10,
    width: '80%',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 10,
  },
  recordingButton: {
    backgroundColor: '#e74c3c',
  },
  disabledButton: {
    opacity: 0.5,
  },
  homeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 25,
    marginTop: 30,
  },
});